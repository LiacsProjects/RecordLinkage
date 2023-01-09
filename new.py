import pandas as pd
import numpy as np
from time import time
import Levenshtein
import csv
import os


"""
Assumptions:


"""


INDEX_GROOM = 30
INDEX_GROOM_FATHER = 48
INDEX_GROOM_MOTHER = 66
INDEX_BRIDE = 84
INDEX_BRIDE_FATHER = 102
INDEX_BRIDE_MOTHER = 120


# df = pd.DataFrame({
#     'col1': ['D', 'B', 'D', 'A', 'C'],
#     # 'col2': [2, 1, 9, 8, 7],
#     # 'col3': [0, 1, 9, 4, 2],
#     # 'col4': ['a', 'B', 'c', 'D', 'e', 'F']
# })


# new = df.sort_values(by=["col1"])

# print(new)
# print("\n", 2, new.iloc[2:])
# print("\n", 2, new.at[0, "col1"])


def unique_file_name(path, extension = ""):
    i = 0
    temp_path = path
    while os.path.exists(temp_path + "." + extension):  #check of het bestand al bestaat
        i += 1
        temp_path = path + " ({})".format(str(i))
    return temp_path + "." + extension



def clean(value):
    return str(value).replace("<NA>", "").strip()


def generate_persons2():

    def get_date(date:str):

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
            # print(e, "date")
            return 0, 0, 0


    def get_age(age_raw:str):
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
            # print(e, "age")
            return 0


    def get_index(role):
        if role == "Bruidegom":
            return INDEX_GROOM
        if role == "Vader bruidegom":
            return INDEX_GROOM_FATHER
        if role == "Moeder bruidegom":
            return INDEX_GROOM_MOTHER
        if role == "Bruid":
            return INDEX_BRIDE
        if role == "Vader bruid":
            return INDEX_BRIDE_FATHER
        if role == "Moeder bruid":
            return INDEX_BRIDE_MOTHER
    

    df_marriage_unfiltered = pd.read_csv(r'data\unprocessed\Huwelijk.csv', sep=";", dtype="string")
    marriages = []
    person_id = 0

    for marriage_unfiltered in df_marriage_unfiltered.itertuples():
        day, month, year = get_date(marriage_unfiltered[27])

        marriage = [
            marriage_unfiltered[0],     # id
            marriage_unfiltered[1],     # uuid
            day, month, year]          # Date

        marriages.append(marriage)


    df_marriage = pd.DataFrame(marriages, columns=[
        "id", 
        "uuid", 
        "dag", 
        "maand", 
        "jaar"])

    df_marriage.to_csv("marriages2.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)





MAX_YEARS_BETWEEN_LINKS = 40
MIN_YEARS_BETWEEN_LINKS = 15
MAX_LEVENSTHEIN = 3

def find_links():
    "zoek certificaat van ouders"
    start = time()
    exceptions = []
    links = []
    year_indexes = {}

    df_marriages = pd.read_csv("marriages.csv", sep=";").sort_values(by=["jaar", "maand", "dag"]).reset_index(drop=True)
    df_persons = pd.read_csv("persons.csv", sep=";")

    for year in range(1811, 1951):
        year_indexes[year] = df_marriages.jaar.searchsorted(year)
    

    def get_name(person_id):
        first_name = df_persons.at[person_id, "voornaam"]
        prefix = df_persons.at[person_id, "tussenvoegsel"]
        last_name = df_persons.at[person_id, "geslachtsnaam"]

        name = []
        if isinstance(first_name, str):
            name.append(first_name)

        if isinstance(prefix, str):
            name.append(prefix)

        if isinstance(last_name, str):
            name.append(last_name)
        return " ".join(name).lower().replace("ch", "g").replace("c", "k").replace("z", "s").replace("ph", "f").replace("ij", "y")


    
    for marriage in df_marriages.itertuples():
        if marriage.Index % 100 == 0:
            print(marriage.jaar, marriage.Index, len(links))

        if not marriage.jaar in range(1811, 1951):
            exceptions.append([marriage.id, marriage.uuid, "year not in correct period or incorrect format used"])
            continue

        year_start = marriage.jaar - MAX_YEARS_BETWEEN_LINKS
        if year_start < 1811:
            year_start = 1811

        year_end = marriage.jaar - MIN_YEARS_BETWEEN_LINKS
        if year_end < 1811:
            year_end = 1811

        year_start_index = year_indexes[year_start]
        year_end_index = year_indexes[year_end]

        df_potential_matches = df_marriages.iloc[year_start_index:year_end_index]


        groom_father_id = marriage.id + 1
        groom_mother_id = marriage.id + 2
        bride_father_id = marriage.id + 4
        bride_mother_id = marriage.id + 5
        
        parents = [[get_name(groom_father_id), get_name(groom_mother_id), groom_father_id, groom_mother_id],
                    [get_name(bride_father_id), get_name(bride_mother_id), bride_father_id, bride_mother_id]]


        # print("length", len(df_potential_matches))
        # print("marriage id", marriage.id)
        for potential_match in df_potential_matches.itertuples():
            groom_id = potential_match.id
            bride_id = potential_match.id + 3

            groom_name = get_name(groom_id)
            bride_name = get_name(bride_id)

            # print(groom_name, bride_name)

            for parent in parents:
                distance = Levenshtein.distance(groom_name + " " + bride_name, parent[0] + " " + parent[1])
            
                if distance <= MAX_LEVENSTHEIN:
                    links.append([marriage.id,                  # id certificate
                        potential_match.id, 
                        groom_id, 
                        parent[2], 
                        bride_id, 
                        parent[3], 
                        distance, 
                        len(groom_name + " " + bride_name), 
                        len(parent[0] + " " + parent[1]),
                        marriage.jaar - potential_match.jaar])
                    continue



        # if marriage.Index > 2:
        if len(links) > 100:
            break

    print(exceptions)
    #     # print(marriage.Index)

    #     df_potential_matches = df_marriages.iloc[:marriage.Index]
    #     for potential_match in df_potential_matches.itertuples():

    #     break

    # exceptions

    df_links = pd.DataFrame(links, columns=[
        "parents_id", 
        "partners_id", 
        "groom", 
        "father", 
        "bride", 
        "mother", 
        "distance", 
        "length partners", 
        "length parents",
        "years_between"])


    
    df_links.to_csv(unique_file_name("results\\links", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


    # print(df_marriages)

    print(f"Run took {round(time() - start, 2)} seconds")


find_links()

