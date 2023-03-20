import pandas as pd
import numpy as np
from time import time
import Levenshtein
import csv
import os
import multiprocessing
import re


MAX_LEVENSTHEIN = 3

AGE_MARRIED_RANGE = {"min": 15,
                     "max": 80}

AGE_MOTHER_RANGE = {"min": 15,
                    "max": 50}

AGE_DEATH_RANGE = {"min": 0,
                    "max": 100}

MODES = {
    1: {"references": [1], "potential_links": [2, 3]},
    2: {"references": [1], "potential_links": [4]},
    3: {"references": [2, 3], "potential_links": [4]},
    4: {"references": [4], "potential_links": [4]},
    5: {"references": [2,3], "potential_links": [6]},
    6: {"references": [4], "potential_links": [6]}
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

        self.df_pairs = pd.read_csv("data\\pairs (6).csv", sep=";")

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
            -- mode 5 for ho-d
            -- mode 6 for b-d
            -------------------------------------
        """))
    
    
    def get_period(self, age=0):
        start = None
        end = None
        
        if self.mode == 1:
            start = AGE_MOTHER_RANGE["min"]
            end = AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"] - AGE_MARRIED_RANGE["min"]
            if age > 14:
                end = AGE_MOTHER_RANGE["max"] - age + AGE_MARRIED_RANGE["max"]
        
        elif self.mode == 2:
            start = max(0, AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]
            if age != 0:
                end = AGE_MOTHER_RANGE["max"] - age
        
        elif self.mode == 3:
            start = AGE_MOTHER_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + AGE_MARRIED_RANGE["min"])
            if age != 0:
                start = AGE_MOTHER_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + age)
                end = AGE_MOTHER_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + age)

        elif self.mode == 4:
            start = AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"]
            end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]
        
        elif self.mode == 5:
            start = AGE_MOTHER_RANGE["min"] + AGE_DEATH_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] + AGE_DEATH_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + AGE_MARRIED_RANGE["min"])
            if age != 0:
                start = AGE_MOTHER_RANGE["min"] + AGE_DEATH_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + age)
                end = AGE_MOTHER_RANGE["max"] + AGE_DEATH_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + age)
                
        elif self.mode == 6:
            pass
        
        return {"start": start, "end": end}


    def filter_pairs(self, mode):
        references = []
        for reference in MODES[mode]["references"]:
            references.append(self.df_pairs[self.df_pairs["role"] == reference])

        potential_links = []
        for potential_link in MODES[mode]["potential_links"]:
            potential_links.append(self.df_pairs[self.df_pairs["role"] == potential_link])

        df_references = pd.concat(references)
        df_potential_links = pd.concat(potential_links).sort_values(by=["year"]).reset_index(drop=True)
        return df_references, df_potential_links


    def find_links_reference(self, reference):
        links_certs = []
        links_persons = []
        # if reference.Index % 1000 == 0:
        #     print(reference.year, reference.Index, len(self.links_certs))

        # Get the age to narrow down potential matches
        reference_age = 0
        if self.mode == 1 or self.mode == 2:
            reference_age = reference.woman_age
        elif self.mode == 3:
            reference_age = reference.child_age

        # Get period where a match can happen
        period_relative = self.get_period(reference_age)
        period = {"start": max(1811, min(1950, reference.year + period_relative["start"])), "end": max(1811, min(1950, reference.year + period_relative["end"]))}

        # Get index of year range
        period_index = {"start": self.year_indexes[period["start"]], "end": self.year_indexes[period["end"]]}

        # Filter potential matches on year and first letters
        df_potential_links_filtered = self.df_potential_links.iloc[period_index["start"]:period_index["end"]]
        df_potential_links_filtered = df_potential_links_filtered[df_potential_links_filtered["first_letters"] == reference.first_letters]

        # Search all potential links for matching names
        for potential_link in df_potential_links_filtered.itertuples():
            # Voor b-b moet er iets bedacht worden om aantal links te verkleinen
            if self.mode == 4:
                if potential_link.uuid == reference.uuid:
                    continue

            distance = Levenshtein.distance(reference.man + " " + reference.woman, potential_link.man + " " + potential_link.woman)
            
            if distance <= MAX_LEVENSTHEIN:
                links_certs.append([
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

                links_persons.append([self.mode, reference.man_uuid, potential_link.man_uuid, "m"])
                links_persons.append([self.mode, reference.woman_uuid, potential_link.woman_uuid, "v"])

                # Link childeren in match
                try:
                    if self.mode == 3 or self.mode == 5 or self.mode == 6:
                        if len(reference.child_uuid) > 0 and len(potential_link.child_uuid) > 0:
                            distance = Levenshtein.distance(reference.child, potential_link.child)

                            if distance <= MAX_LEVENSTHEIN:
                                sex = "mc"
                                if reference.role == 3:
                                    sex = "vc"
                                links_persons.append([self.mode, reference.child_uuid, potential_link.child_uuid, sex])
                except:
                    pass

        return links_certs, links_persons


    def find_links_batch(self, df_references_batch:pd.DataFrame):
        links_certs_batch =  []
        links_persons_batch = []

        for reference in df_references_batch.itertuples():
            links_certs, links_persons = self.find_links_reference(reference)
            links_certs_batch += links_certs
            links_persons_batch += links_persons

        return df_references_batch, links_certs_batch, links_persons_batch


    def find_links(self, mode, cpu_boost=False):
        self.mode = mode
        df_references, self.df_potential_links = self.filter_pairs(mode)

        for year in range(1811, 1951):
            self.year_indexes[year] = self.df_potential_links.year.searchsorted(year)
        
        if cpu_boost:
            df_references_batched = np.array_split(df_references, multiprocessing.cpu_count() * 2)

            with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
                for df_references_batch, links_certs_batch, links_persons_batch in pool.imap_unordered(self.find_links_batch, df_references_batched):
                    self.links_certs += links_certs_batch
                    self.links_persons += links_persons_batch

                    print(re.sub(" +", " ", f"""
                        -------------------------------------
                        Batch has been processed
                        Certificates in batch: {len(df_references_batch.index)}
                        Links in batch: {len(links_certs_batch)}
                        Total amount of links: {len(self.links_certs)}
                    """))
        else:
            for reference in df_references.itertuples():
                links_certs, links_persons = self.find_links_reference(reference)
                self.links_certs += links_certs
                self.links_persons += links_persons

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
        print(re.sub(" +", " ", f"""
            -------------------------------------
            Saved cert links at {path_result_certs}
        """))

        path_result_persons = unique_file_name(f"results\\Links Persons RecordLinker", "csv")
        df_links_persons.to_csv(path_result_persons, sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(re.sub(" +", " ", f"""
            -------------------------------------
            Saved person links at {path_result_persons}
        """))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    linker = RecordLinker()
    # linker.find_links(1, True)
    # linker.find_links(2, True)
    # linker.find_links(3, True)
    # linker.find_links(4, True)
    linker.find_links(5, True)
    # linker.find_links(6, True)
    linker.save_links()

