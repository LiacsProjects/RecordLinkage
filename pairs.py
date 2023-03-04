import pandas as pd
import csv
import os

WHITELIST = set("abcdefghijklmnopqrstuvwxyz ")


def unique_file_name(path, extension = ""):
    i = 0
    temp_path = path
    while os.path.exists(temp_path + "." + extension):  #check of het bestand al bestaat
        i += 1
        temp_path = path + " ({})".format(str(i))
    return temp_path + "." + extension


class GeneratePairs():
    def __init__(self):
        # Read files
        self.df_registrations_marriage = pd.read_csv("data\\Marriages\\marriages.csv", sep=";")
        self.df_persons_marriage = pd.read_csv("data\\Marriages\\persons.csv", sep=";")
        self.df_registrations_birth = pd.read_csv("data\\Births\\births.csv", sep=";")
        self.df_persons_birth = pd.read_csv("data\\Births\\persons.csv", sep=";")

        self.exceptions = []
        self.pairs = []
        self.processed_before = 0


    def pairs_marriage(self):
        self.processed_before = len(self.pairs) - self.processed_before

        for registration_marriage in self.df_registrations_marriage.itertuples():
            year = registration_marriage.jaar

            groom_id = registration_marriage.id * 6
            groom_father_id = registration_marriage.id * 6 + 1
            groom_mother_id = registration_marriage.id * 6 + 2
            bride_id = registration_marriage.id * 6 + 3
            bride_father_id = registration_marriage.id * 6 + 4
            bride_mother_id = registration_marriage.id * 6 + 5

            pairs_id = [[1, groom_id, bride_id, None], [2, groom_father_id, groom_mother_id, groom_id], [3, bride_father_id, bride_mother_id, bride_id]]

            for pair_id in pairs_id:
                try:
                    role = pair_id[0]
                    child = None
                    child_age = 0
                    child_uuid = None

                    man, letter_man = self.get_name_first_letter(pair_id[1], "marriage")
                    woman, letter_woman = self.get_name_first_letter(pair_id[2], "marriage")

                    father_uuid = self.df_persons_marriage.at[pair_id[1], "uuid"]
                    mother_uuid = self.df_persons_marriage.at[pair_id[2], "uuid"]

                    if role != 1:
                        child, _ = self.get_name_first_letter(pair_id[3], "marriage")
                        child_age = int(str(self.df_persons_marriage.at[pair_id[3], "leeftijd"])[:2])
                        child_uuid = self.df_persons_marriage.at[pair_id[3], "uuid"]
                    
                    pair = [year,
                            letter_man + letter_woman,
                            role,
                            man,
                            woman,
                            int(str(self.df_persons_marriage.at[pair_id[2], "leeftijd"])[:2]),
                            child,
                            child_age,
                            registration_marriage.uuid,
                            father_uuid,
                            mother_uuid,
                            child_uuid]
                    
                    self.pairs.append(pair)
                except Exception as e:
                    # print("Exception", pair_id, e)
                    self.exceptions.append(pair_id + [e])



    def pairs_birth(self):
        self.processed_before = len(self.pairs) - self.processed_before

        for registration_birth in self.df_registrations_birth.itertuples():
            year = registration_birth.jaar

            child_id = registration_birth.id * 3
            father_id = registration_birth.id * 3 + 1
            mother_id = registration_birth.id * 3 + 2

            try:
                role = 4
                child, _ = self.get_name_first_letter(child_id, "birth")

                man, letter_man = self.get_name_first_letter(father_id, "birth")
                woman, letter_woman = self.get_name_first_letter(mother_id, "birth")

                pair = [year, 
                        letter_man + letter_woman, 
                        role, 
                        man, 
                        woman, 
                        0,
                        child, 
                        0, 
                        registration_birth.uuid, 
                        self.df_persons_birth.at[father_id, "uuid"], 
                        self.df_persons_birth.at[mother_id, "uuid"],
                        self.df_persons_birth.at[child_id, "uuid"]]
                
                self.pairs.append(pair)

            except Exception as e:
                # print("Exception", [4, father_id, mother_id, child_id], e)
                self.exceptions.append([4, father_id, mother_id, child_id, e])


    def construct_pairs(self):
        self.pairs_marriage()

        print(f"""
        Pairs marriage processed. Total: {len(self.pairs) - self.processed_before}
        ---------------------------------------

        """)

        self.pairs_birth()

        print(f"""
        Pairs birth processed. Total: {len(self.pairs - self.processed_before)}
        ---------------------------------------

        """)

        df_pairs = pd.DataFrame(self.pairs, columns=[
            "year", 
            "first_letters", 
            "role",  
            "man", 
            "woman", 
            "woman_age",
            "child", 
            "child_age", 
            "uuid", 
            "man_uuid",
            "woman_uuid",
            "child_uuid"])

        df_exceptions = pd.DataFrame(self.exceptions, columns=[
            "type",
            "man_id", 
            "woman_id", 
            "child_id", 
            "exception"])
        
        # df_links['first_letters'].value_counts().to_csv("distr.csv", sep=";", quoting=csv.QUOTE_NONNUMERIC)
        df_exceptions.to_csv(unique_file_name("data\\exceptions", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        df_pairs.to_csv(unique_file_name("data\\pairs", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)

        print("All pairs processed. Total:", len(df_pairs.index))
        print("Exceptions:", len(df_exceptions.index))


    def get_name_first_letter(self, person_id, type):
        first_name, prefix, last_name = self.get_name(person_id, type)
        name = " ".join([name for name in [first_name, prefix, last_name] if isinstance(name, str)])
        first_letter = last_name[0]
        return name, first_letter


    def get_name(self, person_id, type):

        def clean(chars):
            if isinstance(chars, str):
                return "".join(filter(WHITELIST.__contains__, str(chars).lower())).replace("ch", "g").replace("c", "k").replace("z", "s").replace("ph", "f").replace("ij", "y")
        
        if type == "marriage":
            df_persons = self.df_persons_marriage
        elif type == "birth":
            df_persons = self.df_persons_birth

        first_name = clean(df_persons.at[person_id, "voornaam"])
        prefix = clean(df_persons.at[person_id, "tussenvoegsel"])
        last_name = clean(df_persons.at[person_id, "geslachtsnaam"])

        return first_name, prefix, last_name


if __name__ == '__main__':
    pairs = GeneratePairs()
    pairs.construct_pairs()

