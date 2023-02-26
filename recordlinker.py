import pandas as pd
import numpy as np
from time import time
import Levenshtein
import csv
import os
import multiprocessing


WHITELIST = set("abcdefghijklmnopqrstuvwxyz ")
MAX_YEARS_BETWEEN_LINKS = 100
MIN_YEARS_BETWEEN_LINKS = 15
MAX_LEVENSTHEIN = 3


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
        self.links_persons = []
        self.links_certs = []
        self.year_indexes = {}

        print(f"""
            -- maximum years between links: {MAX_YEARS_BETWEEN_LINKS}
            -- minimum years between links: {MIN_YEARS_BETWEEN_LINKS}
            -- maximum Levenshtein distance: {MAX_LEVENSTHEIN}

        """)
    

    def cluster_pairs(self):
        self.df_registrations_marriage = pd.read_csv("data\\Marriages\\marriages.csv", sep=";")
        self.df_persons_marriage = pd.read_csv("data\\Marriages\\persons.csv", sep=";")

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

                    man, letter_man = self.get_name_first_letter(pair_id[1])
                    woman, letter_woman = self.get_name_first_letter(pair_id[2])

                    if role != 1:
                        child, _ = self.get_name_first_letter(pair_id[3])
                        child_birth_year = year - self.df_persons_marriage.at[pair_id[3], "leeftijd"] - 1
                    
                    pair = [year, 
                            letter_man + letter_woman, 
                            role, 
                            man, 
                            woman, 
                            child, 
                            child_birth_year, 
                            registration_marriage.uuid, 
                            self.df_persons_marriage.at[pair_id[1], "uuid"], 
                            self.df_persons_marriage.at[pair_id[2], "uuid"]]
                    pairs.append(pair)
                except Exception as e:
                    print("Exception", pair_id, e)


        df_links = pd.DataFrame(pairs, columns=[
            "year", 
            "first_letters", 
            "role", 
            "man", 
            "woman", 
            "child", 
            "child_birth_year", 
            "uuid", 
            "man_uuid",
            "woman_uuid"])

        # df_links['first_letters'].value_counts().to_csv("distr.csv", sep=";", quoting=csv.QUOTE_NONNUMERIC)
        df_links.to_csv(unique_file_name("data\\pairs_marriage", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        print("Length pairs marriage", len(df_links.index))


    def get_name_first_letter(self, person_id):
        first_name, prefix, last_name = self.get_name(person_id)
        name = " ".join([name for name in [first_name, prefix, last_name] if isinstance(name, str)])
        first_letter = last_name[0]
        return name, first_letter


    def get_name(self, person_id):

        def clean(chars):
            if isinstance(chars, str):
                return "".join(filter(WHITELIST.__contains__, str(chars).lower())).replace("ch", "g").replace("c", "k").replace("z", "s").replace("ph", "f").replace("ij", "y")
        
        first_name = clean(self.df_persons_marriage.at[person_id, "voornaam"])
        prefix = clean(self.df_persons_marriage.at[person_id, "tussenvoegsel"])
        last_name = clean(self.df_persons_marriage.at[person_id, "geslachtsnaam"])

        return first_name, prefix, last_name


    def find_links(self):
        self.df_pairs_marriage = pd.read_csv("data\\pairs_marriage.csv", sep=";").sort_values(by=["year"]).reset_index(drop=True)

        for year in range(1811, 1951):
            self.year_indexes[year] = self.df_pairs_marriage.year.searchsorted(year)

        for pair_marriage in self.df_pairs_marriage[self.df_pairs_marriage["role"] == 1].reset_index(drop=True).itertuples():

            if pair_marriage.Index % 100 == 0:
                print(pair_marriage.year, pair_marriage.Index, len(self.links_certs))

            # Get range of years where a match can happen
            year_start = min(1950, pair_marriage.year + MIN_YEARS_BETWEEN_LINKS)
            year_end = min(1950, pair_marriage.year + MAX_YEARS_BETWEEN_LINKS)

            # Get index of year range
            year_start_index = self.year_indexes[year_start]
            year_end_index = self.year_indexes[year_end]

            # Filter potential matches on year, role and first letters
            df_potential_matches = self.df_pairs_marriage.iloc[year_start_index:year_end_index]
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
        
        df_links_certs.to_csv(unique_file_name(f"results\\Links Certs RecordLinker", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        df_links_persons.to_csv(unique_file_name(f"results\\Links Persons RecordLinker", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)

        print(f"""
            -------------------------------------
            Run took {round(time() - self.start, 2)} seconds
            {len(df_links_certs.index)} links found!
        """)



if __name__ == '__main__':
    multiprocessing.freeze_support()
    linker = RecordLinker()
    linker.find_links()

