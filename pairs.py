import pandas as pd
import csv
import os
import unidecode


WHITELIST = set("abcdefghijklmnopqrstuvwxyz")

INDEX_DECEASED = 29
INDEX_RELATION = 48
INDEX_DECEASED_FATHER = 68
INDEX_DECEASED_MOTHER = 87

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
        # self.df_registrations_birth = pd.read_csv("data\\Births\\births.csv", sep=";")
        # self.df_persons_birth = pd.read_csv("data\\Births\\persons.csv", sep=";")
        self.df_deaths = pd.read_csv("data\\unprocessed\\Overlijden.csv", sep=";", dtype="string")

        self.exceptions = []
        self.pairs = []
        self.processed_before = 0


    def get_date(self, date:str):

        def keep_numeric(text):
            return int("".join([ch for ch in text if ch.isnumeric()]))

        try:
            date_list = date.split("-")
            if date[2] == "-":
                index_day, index_month, index_year = 0, 1, 2
            else:
                index_day, index_month, index_year = 2, 1, 0

            return keep_numeric(date_list[index_day]), keep_numeric(date_list[index_month]), keep_numeric(date_list[index_year])

        except Exception as e:
            return 0, 0, 0


    def get_age(self, age_raw:str):
        try:
            age = ''
            for ch in age_raw:
                if ch.isnumeric():  
                    age += ch

            if len(age) > 0:
                return int(age)
            else:
                return 0
        except Exception as e:
            return 0
        

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

                    man, letter_man = self.get_name(pair_id[1], "marriage")
                    woman, letter_woman = self.get_name(pair_id[2], "marriage")

                    father_uuid = self.df_persons_marriage.at[pair_id[1], "uuid"]
                    mother_uuid = self.df_persons_marriage.at[pair_id[2], "uuid"]

                    if role != 1:
                        child, _ = self.get_name(pair_id[3], "marriage")
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
                child, _ = self.get_name(child_id, "birth")

                man, letter_man = self.get_name(father_id, "birth")
                woman, letter_woman = self.get_name(mother_id, "birth")

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


    def pairs_death(self):
        self.processed_before = len(self.pairs) - self.processed_before

        for registration_death in self.df_deaths.itertuples():


            try:
                # print(registration_death[0])
                _, _, year = self.get_date(registration_death[INDEX_DECEASED + 14])

                deceased = None
                deceased_age = 0
                deceased_uuid = None

                try:
                    deceased, _ = self.get_name2(registration_death[INDEX_DECEASED + 9], registration_death[INDEX_DECEASED + 11])  
                    deceased_age = self.get_age(registration_death[INDEX_DECEASED + 12])
                    deceased_uuid = registration_death[INDEX_DECEASED]
                except:
                    pass     
            
                role = 6

                man, letter_man = self.get_name2(registration_death[INDEX_DECEASED_FATHER + 9], registration_death[INDEX_DECEASED_FATHER + 11])
                woman, letter_woman = self.get_name2(registration_death[INDEX_DECEASED_MOTHER + 9], registration_death[INDEX_DECEASED_MOTHER + 11])

                pair = [year,
                        letter_man + letter_woman, 
                        role, 
                        man, 
                        woman, 
                        0,
                        deceased, 
                        deceased_age, 
                        registration_death.uuid, 
                        registration_death[INDEX_DECEASED_FATHER], 
                        registration_death[INDEX_DECEASED_MOTHER],
                        deceased_uuid]
                
                self.pairs.append(pair)

            except Exception as e:
                self.exceptions.append([4, registration_death[INDEX_DECEASED_FATHER], registration_death[INDEX_DECEASED_MOTHER], registration_death[INDEX_DECEASED], e])

            # try:
            #     role = 5

            #     if "|" in registration_death[INDEX_RELATION]:
            #         continue



            #     woman, letter_woman = self.get_name2(mother_id, "birth")

            #     pair = [year,
            #             letter_man + letter_woman, 
            #             role, 
            #             man, 
            #             woman, 
            #             0,
            #             None, 
            #             0, 
            #             registration_birth.uuid, 
            #             self.df_persons_birth.at[father_id, "uuid"], 
            #             self.df_persons_birth.at[mother_id, "uuid"],
            #             None]
                
            #     self.pairs.append(pair)

            # except Exception as e:
            #     # print("Exception", [4, father_id, mother_id, child_id], e)
            #     self.exceptions.append([4, father_id, mother_id, child_id, e])


    def construct_pairs(self):
        # self.pairs_birth()

        print(f"""
        Pairs birth processed. Total: {len(self.pairs) - self.processed_before}
        ---------------------------------------

        """)

        self.pairs_marriage()

        print(f"""
        Pairs marriage processed. Total: {len(self.pairs) - self.processed_before}
        ---------------------------------------

        """)


        self.pairs_death()

        print(f"""
        Pairs death processed. Total: {len(self.pairs) - self.processed_before}
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
        # df_exceptions.to_csv(unique_file_name("data\\exceptions", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        df_pairs.to_csv(unique_file_name("data\\pairs", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)

        print("All pairs processed. Total:", len(df_pairs.index))
        print("Exceptions:", len(df_exceptions.index))


    def get_name(self, person_id, type):

        def clean(chars):
            if isinstance(chars, str):
                chars = str(chars).lower()
                chars = unidecode.unidecode(chars)
                chars = "".join(filter(WHITELIST.__contains__, chars))
                chars = chars.replace("ch", "g").replace("c", "k").replace("z", "s").replace("ph", "f").replace("ij", "y")
                return chars
    

        if type == "marriage":
            df_persons = self.df_persons_marriage
        elif type == "birth":
            df_persons = self.df_persons_birth

        first_names = "".join(sorted([clean(firstname) for firstname in df_persons.at[person_id, "voornaam"].split()]))
        last_name = clean(df_persons.at[person_id, "geslachtsnaam"])

        return first_names + last_name, last_name[0]


    def get_name2(self, first_name, last_name):

        def clean(chars):
            if isinstance(chars, str):
                chars = str(chars).lower()
                chars = unidecode.unidecode(chars)
                chars = "".join(filter(WHITELIST.__contains__, chars))
                chars = chars.replace("ch", "g").replace("c", "k").replace("z", "s").replace("ph", "f").replace("ij", "y")
                return chars

        first_names = "".join(sorted([clean(firstname) for firstname in first_name.split()]))
        last_name = clean(last_name)

        return first_names + last_name, last_name[0]


if __name__ == '__main__':
    pairs = GeneratePairs()
    pairs.construct_pairs()

