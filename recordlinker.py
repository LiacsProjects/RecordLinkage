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

        print(f"""
            -- maximum Levenshtein distance: {MAX_LEVENSTHEIN}

        """)
    
    def get_period(self, link_type, age:int=None):
        start = None
        end = None
        if link_type == "hp-ho":
            start = AGE_MOTHER_RANGE["min"]
            end = AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"] - AGE_MOTHER_RANGE["min"]
            if age != None:
                start = AGE_MOTHER_RANGE["min"]
                end = AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"] - age 
        
        elif link_type == "hp-b":
            start = max(0, AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]
            if age != None:
                start = max(0, AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"])
                end = AGE_MOTHER_RANGE["max"] - age
        
        elif link_type == "ho-b":
            start = AGE_MOTHER_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + AGE_MOTHER_RANGE["min"])
        
        elif link_type == "b-b":
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
                    child_birth_year = None
                    child_uuid = None

                    man, letter_man = self.get_name_first_letter(pair_id[1], "marriage")
                    woman, letter_woman = self.get_name_first_letter(pair_id[2], "marriage")

                    father_uuid = self.df_persons_marriage.at[pair_id[1], "uuid"]
                    mother_uuid = self.df_persons_marriage.at[pair_id[2], "uuid"]

                    if role != 1:
                        child, _ = self.get_name_first_letter(pair_id[3], "marriage")
                        child_birth_year = year - self.df_persons_marriage.at[pair_id[3], "leeftijd"] - 1
                        child_uuid = self.df_persons_marriage.at[pair_id[3], "uuid"]
                    
                    pair = [year, 
                            letter_man + letter_woman, 
                            role, 
                            man, 
                            woman, 
                            child, 
                            self.df_persons_marriage.at[pair_id[2], "leeftijd"],
                            child_birth_year, 
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
                child_birth_year = year

                man, letter_man = self.get_name_first_letter(father_id, "birth")
                woman, letter_woman = self.get_name_first_letter(mother_id, "birth")

                pair = [year, 
                        letter_man + letter_woman, 
                        role, 
                        man, 
                        woman, 
                        0,
                        child, 
                        child_birth_year, 
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
            "child_birth_year", 
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


    def find_links(self):
        self.df_pairs_marriage = pd.read_csv("data\\pairs.csv", sep=";").sort_values(by=["year"]).reset_index(drop=True)

        for year in range(1811, 1951):
            self.year_indexes[year] = self.df_pairs_marriage.year.searchsorted(year)

        for pair_marriage in self.df_pairs_marriage[self.df_pairs_marriage["role"] == 1].reset_index(drop=True).itertuples():

            if pair_marriage.Index % 100 == 0:
                print(pair_marriage.year, pair_marriage.Index, len(self.links_certs))

            # Get period where a match can happen
            period_relative = self.get_period("hp-ho")
            print(pair_marriage)
            print(period_relative)
            period = {"start": min(1950, pair_marriage.year + period_relative["start"]), "end": min(1950, pair_marriage.year + period_relative["end"])}
            print(period)
            # Get index of year range
            period_index = {"start":self.year_indexes[period["start"]], "end": self.year_indexes[period["end"]]}
            print(period_index)
            break
            # Filter potential matches on year, role and first letters
            df_potential_matches = self.df_pairs_marriage.iloc[period_index["start"]:period_index["end"]]
            df_potential_matches = df_potential_matches[df_potential_matches["role"] != 1]
            df_potential_matches = df_potential_matches[df_potential_matches["first_letters"] == pair_marriage.first_letters]

            for potential_match in df_potential_matches.itertuples():
        
                distance = Levenshtein.distance(pair_marriage.man + " " + pair_marriage.woman, potential_match.man + " " + potential_match.woman)
                
                if distance <= MAX_LEVENSTHEIN:
                    self.links_certs.append([
                        pair_marriage.uuid,
                        potential_match.uuid,
                        pair_marriage.man_uuid,
                        potential_match.man_uuid,
                        pair_marriage.woman_uuid,
                        potential_match.woman_uuid,
                        distance, 
                        len(pair_marriage.man + " " + pair_marriage.woman), 
                        len(potential_match.man + " " + potential_match.woman),
                        potential_match.year - pair_marriage.year])

                    self.links_persons.append([potential_match.man_uuid, pair_marriage.man_uuid, "m"])
                    self.links_persons.append([potential_match.woman_uuid, pair_marriage.woman_uuid, "v"])


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
    linker.find_links()
    # linker.cluster_pairs()

