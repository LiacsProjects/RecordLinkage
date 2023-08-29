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

PAIRS = {
    str([1]): {"name": "parents of newborns", "child": True},
    str([2]): {"name": "married couples", "child": False},
    str([3, 4]): {"name": "parents of married couples", "child": True},
    str([5]): {"name": "deceased and partners", "child": False},
    str([6]): {"name": "parents of deceased", "child": True}}

MODES = {
    1: {"references": [1], "potential_links": [1]},
    2: {"references": [1], "potential_links": [6]},
    3: {"references": [2], "potential_links": [1]},
    4: {"references": [2], "potential_links": [3, 4]},
    5: {"references": [2], "potential_links": [6]}, 
    6: {"references": [3, 4], "potential_links": [1]},
    7: {"references": [3, 4], "potential_links": [3, 4]},
    8: {"references": [3, 4], "potential_links": [6]},
    9: {"references": [5], "potential_links": [1]},
    10: {"references": [5], "potential_links": [2]},
    11: {"references": [5], "potential_links": [3, 4]},  
    12: {"references": [5], "potential_links": [5]},
    13: {"references": [5], "potential_links": [6]},    
    14: {"references": [6], "potential_links": [6]}}


def unique_file_name(path, extension = ""):
    i = 0
    temp_path = path
    while os.path.exists(temp_path + "." + extension):  #check of het bestand al bestaat
        i += 1
        temp_path = path + " ({})".format(str(i))
    return temp_path + "." + extension


class RecordLinker():
    def __init__(self):
        print("""
                     /)
            /\___/\ ((
            \`@_@'/  ))
            {_:Y:.}_//""" +  re.sub(" +", " ", f"""
            -----------(_)^-'(_)-----------------
            WELCOME TO THE RECORDLINKER! :)
            -------------------------------------
            -- maximum Levenshtein distance: {MAX_LEVENSTHEIN}"""))
        
        for mode in MODES:
            print(re.sub(" +", " ", 
            f""" -- mode {mode}: '{PAIRS[str(MODES[mode]["references"])]["name"]}' and '{PAIRS[str(MODES[mode]["potential_links"])]["name"]}'"""))

        print(" -------------------------------------")

        self.start = time()
        self.exceptions = []
        self.links_persons = []
        self.links_certs = []
        self.year_indexes = {}

        self.df_pairs = pd.read_csv("RecordLinker\\data\\pairs.csv", sep=";")

        self.max = max(self.df_pairs["year"])
        self.min = 1811

    
    def get_period(self, age=0):
        start = -999
        end = 999
        
        if self.mode == 1:
            start = AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"]
            end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]

        elif self.mode == 3:
            start = max(0, AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]
            if age != 0:
                end = AGE_MOTHER_RANGE["max"] - age

        elif self.mode == 4:
            start = AGE_MOTHER_RANGE["min"]
            end = AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"] - AGE_MARRIED_RANGE["min"]
            if age > 14:
                end = AGE_MOTHER_RANGE["max"] - age + AGE_MARRIED_RANGE["max"]
        
        elif self.mode == 6:
            start = AGE_MOTHER_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + AGE_MARRIED_RANGE["min"])
            if age != 0:
                start = AGE_MOTHER_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + age)
                end = AGE_MOTHER_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + age)

        elif self.mode == 8:
            start = AGE_MOTHER_RANGE["min"] + AGE_DEATH_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] + AGE_DEATH_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + AGE_MARRIED_RANGE["min"])
            if age != 0:
                start = AGE_MOTHER_RANGE["min"] + AGE_DEATH_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + age)
                end = AGE_MOTHER_RANGE["max"] + AGE_DEATH_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + age)
        
        return {"start": start, "end": end}


    def filter_pairs(self, mode):
        references = []
        for reference in MODES[mode]["references"]:
            references.append(self.df_pairs[self.df_pairs["pair"] == reference])

        potential_links = []
        for potential_link in MODES[mode]["potential_links"]:
            potential_links.append(self.df_pairs[self.df_pairs["pair"] == potential_link])

        df_references = pd.concat(references)
        df_potential_links = pd.concat(potential_links).sort_values(by=["year"]).reset_index(drop=True)
        return df_references, df_potential_links


    def find_links_reference(self, reference):
        links_certs = []
        links_persons = []

        # Get period where a match can happen
        period_relative = self.get_period(reference.age)
        period = {"start": max(self.min, min(self.max, reference.year + period_relative["start"])), "end": max(self.min, min(self.max, reference.year + period_relative["end"]))}

        # Get index of year range
        period_index = {"start": self.year_indexes[period["start"]], "end": self.year_indexes[period["end"]]}

        # Filter potential matches on year and first letters
        df_potential_links_filtered = self.df_potential_links.iloc[period_index["start"]:period_index["end"]]
        if MODES[self.mode]["references"] == [5]:
            df_potential_links_filtered = pd.concat([df_potential_links_filtered[df_potential_links_filtered["first_letters"] == reference.first_letters], 
                                                     df_potential_links_filtered[df_potential_links_filtered["first_letters"] == reference.first_letters[::-1]]])
        else:
            df_potential_links_filtered = df_potential_links_filtered[df_potential_links_filtered["first_letters"] == reference.first_letters]
        
        # Search all potential links for matching names
        for potential_link in df_potential_links_filtered.itertuples():
            # Voor aantal modes kan er met zichzelf gelinkt worden. Dit wordt hiermee voorkomen
            if MODES[self.mode]["references"] == MODES[self.mode]["potential_links"]:
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
                    if PAIRS[str(MODES[self.mode]["references"])]["child"] and PAIRS[str(MODES[self.mode]["potential_links"])]["child"]:
                        if len(reference.child_uuid) > 0 and len(potential_link.child_uuid) > 0:
                            distance = Levenshtein.distance(reference.child, potential_link.child)

                            if distance <= MAX_LEVENSTHEIN:
                                sex = "-"
                                links_persons.append([self.mode, reference.child_uuid, potential_link.child_uuid, sex])
                except:
                    pass
            
            else: # Due to the unknown sex of the persons in the 'deceased and partner' pair a link can be found switching the order
                if MODES[self.mode]["references"] == [5]:
                    distance = Levenshtein.distance(reference.woman + " " + reference.man, potential_link.man + " " + potential_link.woman)

                    if distance <= MAX_LEVENSTHEIN:
                        links_certs.append([
                            self.mode,
                            reference.uuid,
                            potential_link.uuid,
                            reference.woman_uuid,
                            potential_link.man_uuid,
                            reference.man_uuid,
                            potential_link.woman_uuid,
                            distance, 
                            len(reference.woman + reference.man), 
                            len(potential_link.man + potential_link.woman),
                            potential_link.year - reference.year])

                        # If both reference pairs and potential links are 5, the sex is not known
                        if MODES[self.mode]["potential_links"] == [5]:
                            links_persons.append([self.mode, reference.woman_uuid, potential_link.man_uuid, "-"])
                            links_persons.append([self.mode, reference.man_uuid, potential_link.woman_uuid, "-"])
                        else:
                            links_persons.append([self.mode, reference.woman_uuid, potential_link.man_uuid, "m"])
                            links_persons.append([self.mode, reference.man_uuid, potential_link.woman_uuid, "v"])

        return links_certs, links_persons


    def find_links_batch(self, df_references_batch:pd.DataFrame):
        links_certs_batch =  []
        links_persons_batch = []

        for reference in df_references_batch.itertuples():
            links_certs, links_persons = self.find_links_reference(reference)
            links_certs_batch += links_certs
            links_persons_batch += links_persons

        return links_certs_batch, links_persons_batch


    def find_links(self, mode, cpu_boost=False):

        def progress_bar(procentage):
            bar_width = 50
            filledLength = int(bar_width * procentage)
            bar = "█" * filledLength + "-" * (bar_width - filledLength)
            print("\r Progress |" + bar, end="")


        print(re.sub(" +", " ", f"""
            Mode {mode}
            Linking '{PAIRS[str(MODES[mode]["references"])]["name"]}' to '{PAIRS[str(MODES[mode]["potential_links"])]["name"]}'
            """))

        self.mode = mode
        df_references, self.df_potential_links = self.filter_pairs(mode)

        for year in range(self.min, self.max + 1):
            self.year_indexes[year] = self.df_potential_links.year.searchsorted(year)
        
        if cpu_boost:
            completed_batches = 0
            df_references_batched = np.array_split(df_references, multiprocessing.cpu_count() * 2)
            progress_bar(0)
            with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
                for links_certs_batch, links_persons_batch in pool.imap_unordered(self.find_links_batch, df_references_batched):
                    completed_batches += 1
                    self.links_certs += links_certs_batch
                    self.links_persons += links_persons_batch

                    progress_bar(completed_batches / (multiprocessing.cpu_count() * 2))
 
        else:
            refs = len(df_references.index)
            progress_bar(0)
            for index, reference in enumerate(df_references.itertuples()):
                links_certs, links_persons = self.find_links_reference(reference)
                self.links_certs += links_certs
                self.links_persons += links_persons

                if index % 1000 == 0:
                    progress_bar(index / refs)
            progress_bar(1)

        print(re.sub(" +", " ", f"""
            -------------------------------------
            Run took {round(time() - self.start, 2)} seconds
            {len(self.links_certs)} links found!
            -------------------------------------"""))


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
        
        path_result_certs = unique_file_name(f"RecordLinker\\results\\RL Links Certs", "csv")
        df_links_certs.to_csv(path_result_certs, sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(re.sub(" +", " ", f"""
            Saved linked certificates at {path_result_certs}"""))

        path_result_persons = unique_file_name("RecordLinker\\results\\RL Links Persons", "csv")
        df_links_persons.to_csv(path_result_persons, sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(re.sub(" +", " ", f"""
            Saved linked persons at {path_result_persons}"""))


if __name__ == "__main__":
    multiprocessing.freeze_support()
    linker = RecordLinker()
    for mode in range(1,15):
        linker.find_links(mode, True)
        break

    linker.save_links()

