import pandas as pd
import numpy as np
from time import time
import Levenshtein
import csv
import os
import multiprocessing

"""
Assumptions:

Parents are married within a given period relative to the marriage of the children
This period is declared in the constants given below
"""

MAX_YEARS_BETWEEN_LINKS = 40
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
        self.exceptions = []
        self.links = []
        self.year_indexes = {}

        self.df_marriages = pd.read_csv("data\\marriages.csv", sep=";").sort_values(by=["jaar", "maand", "dag"]).reset_index(drop=True)
        self.df_persons_marriages = pd.read_csv("data\\persons.csv", sep=";")
        self.df_births = pd.read_csv("data\\persons.csv", sep=";").sort_values(by=["jaar", "maand", "dag"]).reset_index(drop=True)
        self.df_persons_births = pd.read_csv("data\\persons.csv", sep=";")

        self.total_certificates = len(self.df_births.index)

        print(f"""
            Linking {self.total_certificates} certificates
            -- maximum years between links: {MAX_YEARS_BETWEEN_LINKS}
            -- maximum Levenshtein distance: {MAX_LEVENSTHEIN}

        """)


    def get_name(self, person_id):
        first_name = self.df_persons.at[person_id, "voornaam"]
        prefix = self.df_persons.at[person_id, "tussenvoegsel"]
        last_name = self.df_persons.at[person_id, "geslachtsnaam"]

        name = []
        if isinstance(first_name, str):
            name.append(first_name)

        if isinstance(prefix, str):
            name.append(prefix)

        if isinstance(last_name, str):
            name.append(last_name)
        return " ".join(name).lower().replace("ch", "g").replace("c", "k").replace("z", "s").replace("ph", "f").replace("ij", "y")


    def find_linking_certificates(self, df_marriages):
        links = []
        matches = []
        exceptions = []
        count = 0
        for marriage in df_marriages.itertuples():
            # if count % 1000 == 0:
            #     print(len(links), count)
                # print(round(count / len(df_marriages.index), 3), os.getpid(), len(links))
            
            # if len(links) > 50:
            #     break

            count += 1

            # if marriage.id % 100 == 0:
                # print(marriage.jaar, marriage.id, len(links))

            if not marriage.jaar in range(1811, 1951):
                exceptions.append([marriage.id, marriage.uuid, "year not in correct period or incorrect format used"])
                continue

            year_start = marriage.jaar - MAX_YEARS_BETWEEN_LINKS
            if year_start < 1811:
                year_start = 1811

            year_end = marriage.jaar - MIN_YEARS_BETWEEN_LINKS
            if year_end < 1811:
                year_end = 1811

            year_start_index = self.year_indexes[year_start]
            year_end_index = self.year_indexes[year_end]

            df_potential_matches = self.df_marriages.iloc[year_start_index:year_end_index]


            groom_father_id = marriage.id * 6 + 1
            groom_mother_id = marriage.id * 6 + 2
            bride_father_id = marriage.id * 6 + 4
            bride_mother_id = marriage.id * 6 + 5
            
            parents = [[self.get_name(groom_father_id), self.get_name(groom_mother_id), groom_father_id, groom_mother_id],
                        [self.get_name(bride_father_id), self.get_name(bride_mother_id), bride_father_id, bride_mother_id]]

            for potential_match in df_potential_matches.itertuples():
                groom_id = potential_match.id * 6
                bride_id = potential_match.id * 6 + 3

                groom_name = self.get_name(groom_id)
                bride_name = self.get_name(bride_id)

                for parent in parents:
                    distance = Levenshtein.distance(groom_name + " " + bride_name, parent[0] + " " + parent[1])
                
                    if distance <= MAX_LEVENSTHEIN:
                        # print(groom_name + " " + bride_name, parent[0] + " " + parent[1])
                        links.append([
                            marriage.id,                  # id certificate parents
                            potential_match.id,           # id certificate partners
                            groom_id, 
                            parent[2], 
                            bride_id, 
                            parent[3], 
                            distance, 
                            len(groom_name + " " + bride_name), 
                            len(parent[0] + " " + parent[1]),
                            marriage.jaar - potential_match.jaar])

                        matches.append([self.df_persons.at[groom_id, parent[2], "m"]])
                        matches.append([self.df_persons.at[bride_id, parent[3], "v"]])
                        continue
                        
        return links, exceptions, count


    def find_links(self):
        for year in range(1811, 1951):
            self.year_indexes[year] = self.df_marriages.jaar.searchsorted(year)

        splitted_dfs_marriages = np.array_split(self.df_marriages, multiprocessing.cpu_count() * 2)

        with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
            for links, exceptions, amount_of_certificates in pool.imap_unordered(self.find_linking_certificates, splitted_dfs_marriages):
                self.links += links
                self.exceptions += exceptions

                print(f"""
                    -------------------------------------
                    Batch has been processed
                    Certificates in batch: {amount_of_certificates}
                    Links in batch: {len(links)}
                    Total amount of links: {len(self.links)}
                """)

        df_links = pd.DataFrame(self.links, columns=[
            "parents_id", 
            "birth_id", 
            "groom", 
            "father", 
            "bride", 
            "mother", 
            "distance", 
            "length partners", 
            "length parents",
            "years_between"])

        df_links.to_csv(unique_file_name(f"results\\Links RecordLinker {MIN_YEARS_BETWEEN_LINKS}-{MAX_YEARS_BETWEEN_LINKS}", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)

        print(f"""
            -------------------------------------
            Run took {round(time() - self.start, 2)} seconds
            {len(df_links.index)} links found!
        """)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    linker = RecordLinker()
    linker.find_links()

