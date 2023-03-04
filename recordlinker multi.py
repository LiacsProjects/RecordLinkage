import pandas as pd
import numpy as np
from time import time
import Levenshtein
import csv
import os
import multiprocessing
import re


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

        # self.df_pairs = pd.read_csv("data\\pairs.csv", sep=";")

        print("""
                    /)
            /\___/\ ((
            \`@_@'/  ))
            {_:Y:.}_//""" +  re.sub(" +", " ", f"""
            -----------(_)^-'(_)-----------------
            WELCOME TO THE RECORDLINKER! :)
            -------------------------------------
            -- maximum Levenshtein distance: {MAX_LEVENSTHEIN}
            -- mode 1 for hp-ho
            -- mode 2 for hp-b
            -- mode 3 for ho-b
            -- mode 4 for b-b
            -------------------------------------
        """))
    
    
    def get_period(self, age=0):
        start = None
        end = None
        if self.mode == 1:
            start = AGE_MOTHER_RANGE["min"]
            end = AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"] - AGE_MOTHER_RANGE["min"]
            if age > 14:
                start = AGE_MOTHER_RANGE["min"]
                end = AGE_MOTHER_RANGE["max"] - age + AGE_MARRIED_RANGE["max"]
        
        elif self.mode == 2:
            start = max(0, AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]
            if age != None:
                start = max(0, AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"])
                end = AGE_MOTHER_RANGE["max"] - age
        
        elif self.mode == 3:
            start = AGE_MOTHER_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + AGE_MOTHER_RANGE["min"])
        
        elif self.mode == 4:
            start = AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"]
            end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]
        
        return {"start": start, "end": end}


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


    def find_links_reference(self, reference):
        if reference.Index % 1000 == 0:
            print(reference.year, reference.Index, len(self.links_certs))

        # Get period where a match can happen
        period_relative = self.get_period(reference.woman_age)
        period = {"start": max(1811, min(1950, reference.year + period_relative["start"])), "end": max(1811, min(1950, reference.year + period_relative["end"]))}

        # Get index of year range
        period_index = {"start": self.year_indexes[period["start"]], "end": self.year_indexes[period["end"]]}

        # Filter potential matches on year and first letters
        df_potential_links_filtered = self.df_potential_links.iloc[period_index["start"]:period_index["end"]]
        df_potential_links_filtered = df_potential_links_filtered[df_potential_links_filtered["first_letters"] == reference.first_letters]

        for potential_link in df_potential_links_filtered.itertuples():
            # Voor b-b moet er iets bedacht worden om aantal links te verkleinen
            if self.mode == 4:
                if potential_link.uuid == reference.uuid:
                    continue
                
                if [self.mode, potential_link.man_uuid, reference.man_uuid, "m"] in self.links_persons:
                    continue

            distance = Levenshtein.distance(reference.man + " " + reference.woman, potential_link.man + " " + potential_link.woman)
            
            if distance <= MAX_LEVENSTHEIN:
                self.links_certs.append([
                    self.mode,
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

                self.links_persons.append([self.mode, reference.man_uuid, potential_link.man_uuid, "m"])
                self.links_persons.append([self.mode, reference.woman_uuid, potential_link.woman_uuid, "v"])


    def find_links_batch(self, df_reference_batch:pd.DataFrame):
        for reference in df_reference_batch.itertuples():
            self.find_links_reference(reference)
        return df_reference_batch


    def find_links(self, mode, cpu_boost=False):
        self.mode = mode
        df_references, self.df_potential_links = self.filter_pairs(mode)

        for year in range(1811, 1951):
            self.year_indexes[year] = self.df_potential_links.year.searchsorted(year)
        
        if cpu_boost:
            df_references_batched = np.array_split(df_references, multiprocessing.cpu_count() * 2)

            with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
                for df_reference_batch in pool.imap_unordered(self.find_links_batch, df_references_batched):

                    print(re.sub(" +", " ", f"""
                        -------------------------------------
                        Batch has been processed
                        Certificates in batch: {len(df_reference_batch.index)}
                        Total amount of links: {len(self.links_certs)}
                    """))
        else:
            for reference in df_references.itertuples():
                self.find_links_reference(reference)

        print(re.sub(" +", " ", f"""
            -------------------------------------
            Run took {round(time() - self.start, 2)} seconds
            {len(self.links_certs)} links found!
        """))


    def save_links(self):
        df_links_certs = pd.DataFrame(self.links_certs, columns=[
            "mode",
            "reference_uuid", 
            "potential_link_uuid", 
            "man_uuid", 
            "man_link_uuid", 
            "woman_uuid", 
            "woman_link_uuid", 
            "distance", 
            "length_reference", 
            "length_link",
            "years_between"])

        df_links_persons = pd.DataFrame(self.links_persons, columns=[
            "mode",
            "reference_uuid",
            "link_uuid", 
            "sex"])
        
        path_result_certs = unique_file_name(f"results\\Links Certs RecordLinker", "csv")
        df_links_certs.to_csv(path_result_certs, sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(re.sub(' +', f"""
            -------------------------------------
            Saved person link at {path_result_certs}
        """))

        path_result_persons = unique_file_name(f"results\\Links Persons RecordLinker", "csv")
        df_links_persons.to_csv(path_result_persons, sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(re.sub(' +', f"""
            -------------------------------------
            Saved person link at {path_result_persons}
        """))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    linker = RecordLinker()
    # linker.find_links(1, True)
    # linker.save_links()

