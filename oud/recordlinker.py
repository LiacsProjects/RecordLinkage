import polars as pl
import numpy as np
from time import time
import Levenshtein
import csv
import os
import multiprocessing
import re
import math

MAX_LEVENSTHEIN = 20

AGE_MARRIED_RANGE = {"min": 15,
                     "max": 80}

AGE_MOTHER_RANGE = {"min": 15,
                    "max": 50}

AGE_DEATH_RANGE = {"min": 0,
                    "max": 100}

MODES = {
    1: {"references": [1], "potential_links": [2, 3]}, # 1 
    2: {"references": [1], "potential_links": [4]}, # 2
    3: {"references": [1], "potential_links": [5]},
    4: {"references": [1], "potential_links": [6]}, 

    5: {"references": [2, 3], "potential_links": [2, 3]},
    6: {"references": [2, 3], "potential_links": [4]}, # 3
    7: {"references": [2, 3], "potential_links": [5]},  
    8: {"references": [2, 3], "potential_links": [6]}, # 5

    9: {"references": [4], "potential_links": [4]}, # 4
    10: {"references": [4], "potential_links": [5]},
    11: {"references": [4], "potential_links": [6]}, # 6

    12: {"references": [5], "potential_links": [5]},
    13: {"references": [5], "potential_links": [6]},

    14: {"references": [6], "potential_links": [6]},
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

        self.df_pairs = pl.read_parquet("data\\pairs.pq")

        print(r"""
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
        start = -999
        end = 999
        
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
        
        elif self.mode == 6:
            start = AGE_MOTHER_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + AGE_MARRIED_RANGE["min"])
            if age != 0:
                start = AGE_MOTHER_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + age)
                end = AGE_MOTHER_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + age)

        elif self.mode == 9:
            start = AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"]
            end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]
        
        elif self.mode == 8:
            start = AGE_MOTHER_RANGE["min"] + AGE_DEATH_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] + AGE_DEATH_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + AGE_MARRIED_RANGE["min"])
            if age != 0:
                start = AGE_MOTHER_RANGE["min"] + AGE_DEATH_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + age)
                end = AGE_MOTHER_RANGE["max"] + AGE_DEATH_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + age)
                
        elif self.mode == 11:
            pass
        
        return {"start": start, "end": end}


    def filter_pairs(self, mode):
        references = []
        for reference in MODES[mode]["references"]:
            references.append(self.df_pairs.filter([pl.col("role") == reference]))

        potential_links = []
        for potential_link in MODES[mode]["potential_links"]:
            potential_links.append(self.df_pairs.filter([pl.col("role") == reference]))

        df_references: pl.DataFrame = pl.concat(references)
        df_potential_links: pl.DataFrame = pl.concat(potential_links)
        df_potential_links = df_potential_links.sort(by=["year"])
        return df_references, df_potential_links


    def find_links_reference(self, reference: dict):
        links_certs = []
        links_persons = []
        # if reference.Index % 1000 == 0:
        #     print(reference.year, reference.Index, len(self.links_certs))

        # Get period where a match can happen
        period_relative = self.get_period(reference["age"])
        period = {"start": max(1811, min(1950, reference["year"] + period_relative["start"])), "end": max(1811, min(1950, reference["year"] + period_relative["end"]))}

        # Get index of year range
        period_index = {"start": self.year_indexes[period["start"]], "end": self.year_indexes[period["end"]]}

        # Filter potential matches on year and first letters
        df_potential_links_filtered = self.df_potential_links[period_index["start"]:period_index["end"]]
        df_potential_links_filtered = df_potential_links_filtered.filter(pl.col("first_letters") == reference["first_letters"])

        # Search all potential links for matching names
        for potential_link in df_potential_links_filtered.iter_rows(named=True):
            # Voor aantal modes kan er met zichzelf gelinkt worden. Dit wordt hiermee voorkomen
            if self.mode in [5, 9, 12, 14]:
                if potential_link["uuid"] == reference["uuid"]:
                    continue

            distance = Levenshtein.distance(reference["man"] + " " + reference["woman"], potential_link["man"] + " " + potential_link["woman"])
            
            if distance <= MAX_LEVENSTHEIN:
                links_certs.append([
                    self.mode,
                    reference["uuid"],
                    potential_link["uuid"],
                    reference["man_uuid"],
                    potential_link["man_uuid"],
                    reference["woman_uuid"],
                    potential_link["woman_uuid"],
                    distance, 
                    len(reference["man"] + " " + reference["woman"]), 
                    len(potential_link["man"] + " " + potential_link["woman"]),
                    potential_link["year"] - reference["year"]])

                links_persons.append([self.mode, reference["man_uuid"], potential_link["man_uuid"], "m"])
                links_persons.append([self.mode, reference["woman_uuid"], potential_link["woman_uuid"], "v"])

                # Link childeren in match
                try:
                    if self.mode in [5, 6, 8, 11]:
                        if len(reference["child_uuid"]) > 0 and len(potential_link["child_uuid"]) > 0:
                            distance = Levenshtein.distance(reference["child"], potential_link["child"])

                            if distance <= MAX_LEVENSTHEIN:
                                sex = "c"
                                links_persons.append([self.mode, reference["child_uuid"], potential_link["child_uuid"], sex])
                except:
                    pass

        return links_certs, links_persons


    def find_links_batch(self, df_references_batch:pl.DataFrame):
        links_certs_batch =  []
        links_persons_batch = []

        for reference in df_references_batch.iter_rows(named=True):
            links_certs, links_persons = self.find_links_reference(reference)
            links_certs_batch += links_certs
            links_persons_batch += links_persons

        return df_references_batch, links_certs_batch, links_persons_batch


    def find_links(self, mode, cpu_boost=False):
        self.mode = mode
        df_references, self.df_potential_links = self.filter_pairs(mode)

        for year in range(1811, 1951):
            self.year_indexes[year] = self.df_potential_links["year"].search_sorted(year)
        
        if cpu_boost:
            aantal = multiprocessing.cpu_count() * 2

            aantal_regels = math.floor(df_references.shape[0] / aantal)
            slices = []
            start = 0
            for i in range(aantal):
                if i == aantal-1:
                    slices.append(slice(start, start + aantal_regels + df_references.shape[0] % aantal))
                else:
                    slices.append(slice(start, start + aantal_regels))
                start += aantal_regels

            df_references_batched = [
                df_references[slice] for slice in slices
            ]

            # breakpoint()
            # df_references_batched = np.array_split(df_references, )

            with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
                for df_references_batch, links_certs_batch, links_persons_batch in pool.imap_unordered(self.find_links_batch, df_references_batched):
                    self.links_certs += links_certs_batch
                    self.links_persons += links_persons_batch

                    print(re.sub(" +", " ", f"""
                        -------------------------------------
                        Batch has been processed
                        Certificates in batch: {df_references_batch.shape[0]}
                        Links in batch: {len(links_certs_batch)}
                        Total amount of links: {len(self.links_certs)}
                    """))
        else:
            for reference in df_references.iter_rows(named=True):
                links_certs, links_persons = self.find_links_reference(reference)
                self.links_certs += links_certs
                self.links_persons += links_persons

        print(re.sub(" +", " ", f"""
            -------------------------------------
            Run took {round(time() - self.start, 2)} seconds
            {len(self.links_certs)} links found!
        """))


    def save_links(self):
        df_links_certs = pl.DataFrame(
            self.links_certs,
            orient="row", schema=[
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
                "years_between",
            ]
        )
        df_links_persons = pl.DataFrame(
            self.links_persons,
            orient="row",
            schema=[
                "mode",
                "reference_uuid",
                "link_uuid", 
                "sex",
            ]
        )
        path_result_certs = unique_file_name(f"results\\RL Links Certs", "pq")
        df_links_certs.write_parquet(path_result_certs)
        # df_links_certs.write_csv(path_result_certs, separator=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(re.sub(" +", " ", f"""
            -------------------------------------
            Saved cert links at {path_result_certs}
        """))

        path_result_persons = unique_file_name(f"results\\RL Links Persons", "pq")
        df_links_persons.write_parquet(path_result_persons)
        # df_links_persons.write_csv(path_result_persons, separator=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(re.sub(" +", " ", f"""
            -------------------------------------
            Saved person links at {path_result_persons}
        """))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    linker = RecordLinker()
    # linker.find_links(1, True)
    linker.find_links(2, True)
    linker.find_links(3, True)
    linker.find_links(4, True)
    linker.find_links(5, True)
    linker.find_links(6, True)
    linker.find_links(7, True)
    # linker.find_links(8, True)
    # linker.find_links(9, True)
    # linker.find_links(10, True)
    # linker.find_links(11, True)
    # linker.find_links(12, True)
    # linker.find_links(13, True)
    # linker.find_links(14, True)
    linker.save_links()

