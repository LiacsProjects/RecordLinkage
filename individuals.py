# https://stackoverflow.com/questions/57512155/how-to-draw-a-tree-more-beautifully-in-networkx

import Levenshtein
import csv
import os
import pandas as pd

FORMAT = "svg"
DPI = 300


def unique_file_name(path, extension = ""):
    i = 0
    temp_path = path
    while os.path.exists(temp_path + "." + extension):  #check of het bestand al bestaat
        i += 1
        temp_path = path + " ({})".format(str(i))
    return temp_path + "." + extension


def clean(value):
    return str(value).replace("<NA>", "").strip()


def construct_person_links():
    df_marriages = pd.read_csv("marriages.csv", sep=";", dtype="string")
    df_persons = pd.read_csv("persons.csv", sep=";", dtype="string")
    df_matches = pd.read_csv("clean matches.csv", sep=";")

    def get_name(uuid, role):
        try:
            person = df_persons.loc[(df_persons["uuid"] == uuid) & (df_persons["rol"] == role)].iloc[0]
            name = " ".join(" ".join([clean(person["voornaam"]), clean(person["tussenvoegsel"]), clean(person["geslachtsnaam"])]).split())
            # print(name, role)
            return name
        except:

            return ''
        
        # print("len", len(person))
 
    # double = df_persons.pivot_table(index=['uuid', "rol"], aggfunc='size')
    # print(len(double), len(df_persons))

    # print("unique", df_persons["uuid"].is_unique)

    links = []
    for match in df_matches.itertuples():
        ids = []

        marriage_parents = df_marriages.loc[df_marriages["uuid"] == match[1]].iloc[0]
        marriage_partners = df_marriages.loc[df_marriages["uuid"] == match[2]].iloc[0]

        parents = [marriage_parents["vader_bruidegom_uuid"], marriage_parents["moeder_bruidegom_uuid"], marriage_parents["vader_bruid_uuid"], marriage_parents["moeder_bruid_uuid"]]
        partners = [marriage_partners["bruidegom_uuid"], marriage_partners["bruid_uuid"]]

        partners_string = get_name(partners[0], "Bruidegom") + " " + get_name(partners[1], "Bruid")
        groom_parents_string = get_name(parents[0], "Vader bruidegom") + " " + get_name(parents[1], "Moeder bruidegom")
        bride_parents_string = get_name(parents[2], "Vader bruid") + " " + get_name(parents[3], "Moeder bruid")

        if Levenshtein.distance(partners_string, groom_parents_string) < Levenshtein.distance(partners_string, bride_parents_string):
            links.append([parents[0], partners[0] , "m"])
            links.append([parents[1], partners[1], "v"])
        else:
            links.append([parents[2], partners[0], "m"])
            links.append([parents[3], partners[1], "v"])

        # print(links)
        if len(links) % 1000 == 0:
            print(len(links))
            # break

    df_links = pd.DataFrame(links, columns=["parent_id", "partner_id", "sex"])
    df_links.to_csv("links.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


construct_person_links()

