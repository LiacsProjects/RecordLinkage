import pandas as pd
import numpy as np
from time import time
import Levenshtein
import csv
import os
import multiprocessing




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
            Linking certificates
            -- maximum years between links: 
            -- maximum Levenshtein distance: 

        """)


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

        df_links.to_csv(unique_file_name(f"results\\Links RecordLinker", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)

        print(f"""
            -------------------------------------
            Run took {round(time() - self.start, 2)} seconds
            {len(df_links.index)} links found!
        """)



print(3 % 3)


# if __name__ == '__main__':
#     multiprocessing.freeze_support()
#     linker = RecordLinker()
#     linker.find_links()