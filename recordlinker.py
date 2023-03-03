import pandas as pd
import numpy as np
from time import time
import Levenshtein
import csv
import os
import multiprocessing


WHITELIST = set("abcdefghijklmnopqrstuvwxyz ")
MAX_LEVENSTHEIN = 3

AGE_MARRIED_RANGE = {"min": 15,
                     "max": 70}

AGE_MOTHER_RANGE = {"min": 15,
                    "max": 45}

MODES = {
    1: {"references": [1], "potential_links": [2, 3]},
    2: {"references": [1], "potential_links": [4]},
    3: {"references": [2, 3], "potential_links": [4]},
    4: {"references": [4], "potential_links": [4]},
}


def unique_file_name(path, extension = ""):
    i = 0
    temp_path = path
    while os.path.exists(temp_path + "." + extension):  #check of het bestand al bestaat
        i += 1
        temp_path = path + " ({})".format(str(i))
    return temp_path + "." + extension


class RecordLinker():
    def __init__(self):
        self.start = time()
        self.exceptions = []
        self.links_persons = []
        self.links_certs = []
        self.year_indexes = {}

        self.df_pairs = pd.read_csv("data\\pairs.csv", sep=";")

        print(f"""
            -- maximum Levenshtein distance: {MAX_LEVENSTHEIN}
            -- mode 1 for hp-ho
            -- mode 2 for hp-b
            -- mode 3 for ho-b
            -- mode 4 for b-b
        """)
    
    
    def get_period(self, mode, age):
        start = None
        end = None
        if mode == 1:
            start = AGE_MOTHER_RANGE["min"]
            end = AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"] - AGE_MOTHER_RANGE["min"]
            if age > 14:
                start = AGE_MOTHER_RANGE["min"]
                end = AGE_MOTHER_RANGE["max"] - age + AGE_MARRIED_RANGE["max"]
        
        elif mode == 2:
            start = max(0, AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]
            if age != None:
                start = max(0, AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"])
                end = AGE_MOTHER_RANGE["max"] - age
        
        elif mode == 3:
            start = AGE_MOTHER_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + AGE_MOTHER_RANGE["min"])
        
        elif mode == 4:
            start = AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"]
            end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]
        
        return {"start": start, "end": end}


    def cluster_pairs(self):
        self.df_registrations_marriage = pd.read_csv("data\\Marriages\\marriages.csv", sep=";")
        self.df_persons_marriage = pd.read_csv("data\\Marriages\\persons.csv", sep=";")
        self.df_registrations_birth = pd.read_csv("data\\Births\\births.csv", sep=";")
        self.df_persons_birth = pd.read_csv("data\\Births\\persons.csv", sep=";")

        pairs = []
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
                    
                    pairs.append(pair)
                except Exception as e:
                    # print("Exception", pair_id, e)
                    self.exceptions.append(pair_id + [e])


        print(f"""
        Pairs marriage processed. Total: {len(pairs)}
        ---------------------------------------

        """)

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
                
                pairs.append(pair)

            except Exception as e:
                # print("Exception", [4, father_id, mother_id, child_id], e)
                self.exceptions.append([4, father_id, mother_id, child_id, e])


        df_pairs = pd.DataFrame(pairs, columns=[
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


    def filter_pairs(self, mode):
        references = []
        for reference in MODES[mode]["references"]:
            references.append(self.df_pairs[self.df_pairs["role"] == reference])

        potential_links = []
        for potential_link in MODES[mode]["potential_links"]:
            potential_links.append(self.df_pairs[self.df_pairs["role"] == potential_link])

        df_references = pd.concat(references).sort_values(by=["year"]).reset_index(drop=True)
        df_potential_links = pd.concat(potential_links).sort_values(by=["year"]).reset_index(drop=True)
        return df_references, df_potential_links


    def find_links(self, mode):

        df_references, df_potential_links = self.filter_pairs(mode)
        print(df_references["role"])
        print(df_potential_links["role"])

        for year in range(1811, 1951):
            self.year_indexes[year] = df_potential_links.year.searchsorted(year)


        for reference in df_references.itertuples():

            if reference.Index % 100 == 0:
                print(reference.year, reference.Index, len(self.links_certs))

            # Get period where a match can happen
            # print("age", reference.woman_age)
            period_relative = self.get_period(mode, reference.woman_age)
            # print(reference)
            # print(period_relative)
            period = {"start": max(1811, min(1950, reference.year + period_relative["start"])), "end": max(1811, min(1950, reference.year + period_relative["end"]))}
            # print(period)
            # Get index of year range
            period_index = {"start": self.year_indexes[period["start"]], "end": self.year_indexes[period["end"]]}
            # print(period_index)

            # Filter potential matches on year and first letters
            # print(len(df_potential_links.index))
            df_potential_links_filtered = df_potential_links.iloc[period_index["start"]:period_index["end"]]
            # print(len(df_potential_links.index))
            df_potential_links_filtered = df_potential_links_filtered[df_potential_links_filtered["first_letters"] == reference.first_letters]
            # print(len(df_potential_links.index))

            for potential_link in df_potential_links_filtered.itertuples():
                # print(potential_link, "\n--------------------------------\n")
                distance = Levenshtein.distance(reference.man + " " + reference.woman, potential_link.man + " " + potential_link.woman)
                
                if distance <= MAX_LEVENSTHEIN:
                    self.links_certs.append([
                        reference.uuid,
                        potential_link.uuid,
                        reference.man_uuid,
                        potential_link.man_uuid,
                        reference.woman_uuid,
                        potential_link.woman_uuid,
                        distance, 
                        len(reference.man + " " + reference.woman), 
                        len(potential_link.man + " " + potential_link.woman),
                        potential_link.year - reference.year])

                    self.links_persons.append([potential_link.man_uuid, reference.man_uuid, "m"])
                    self.links_persons.append([potential_link.woman_uuid, reference.woman_uuid, "v"])


        print(len(self.links_certs))
        df_links_certs = pd.DataFrame(self.links_certs, columns=[
            "partners_id", 
            "parents_id", 
            "groom", 
            "father", 
            "bride", 
            "mother", 
            "distance", 
            "length partners", 
            "length parents",
            "years_between"])

        df_links_persons = pd.DataFrame(self.links_persons, columns=[
            "parent_uuid",
            "partner_uuid", 
            "sex"])
        
        # df_links_certs.to_csv(unique_file_name(f"results\\Links Certs RecordLinker", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        # df_links_persons.to_csv(unique_file_name(f"results\\Links Persons RecordLinker", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)

        print(f"""
            -------------------------------------
            Run took {round(time() - self.start, 2)} seconds
            {len(df_links_certs.index)} links found!
        """)



if __name__ == '__main__':
    multiprocessing.freeze_support()
    linker = RecordLinker()
    linker.find_links(1)
    # linker.cluster_pairs()

