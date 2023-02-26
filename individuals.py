# https://stackoverflow.com/questions/57512155/how-to-draw-a-tree-more-beautifully-in-networkx

import Levenshtein
import csv
import os
import pandas as pd
from datetime import datetime

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


def construct_person_links_births():
    df_links = pd.read_csv("data\\links b uuid.csv", sep=";")
    df_marriages = pd.read_csv("data\\marriages met uuid.csv", sep=";")
    df_births = pd.read_csv("data\\unprocessed\\Geboorte.csv", sep=";", dtype="string")

    person_links = []

    for link in df_links.itertuples():
        birth = df_births.loc[df_births['uuid'] == link.birth_id].iloc[0]
        marriage = df_marriages.loc[df_marriages['uuid'] == link.marriage_id].iloc[0]

        father = birth["Vader-uuid"]
        mother = birth["Moeder-uuid"]

        groom = marriage["bruidegom_uuid"]
        bride = marriage["bruid_uuid"]

        person_links.append([father, groom, "m"])
        person_links.append([mother, bride, "v"])

    df_person_links = pd.DataFrame(person_links, columns=["parent_id", "partners_id", "sex"])
    df_person_links.to_csv("data\\links b persons.csv", sep=",", index=False, quoting=csv.QUOTE_NONNUMERIC)


    # df_marriages = pd.read_csv("data\\burgerLinker\\Marriages\\registrations.csv", sep=";", dtype="string")
    # df_births = pd.read_csv("data\\burgerLinker\\Births\\registrations.csv", sep=";", dtype="string")
    # df_links = pd.read_csv("data\\links b.csv", sep=",")
    # df_marriages = pd.read_csv("data\\burgerLinker\\Marriages\\persons.csv", sep=";", dtype="string")
    # df_births = pd.read_csv("data\\burgerLinker\\Births\\persons.csv", sep=";", dtype="string")

    # links_uuid = []
    # for link in df_links.itertuples():
    #     # print(link)
    #     # link.id_certificate_newbornParents
    #     # link.id_certificate_partners
    #     try:
    #         marriage_uuid = df_marriages.at[link.id_certificate_partners - 1, "registration_seq"]
    #         birth_uuid = df_births.at[link.id_certificate_newbornParents - 1_000_001, "registration_seq"]

    #         links_uuid.append([birth_uuid, marriage_uuid])
    #     exc

        # father = (int(link.id_certificate_newbornParents) - 1_000_000 - 1) * 3 + 2
        # mother = (int(link.id_certificate_newbornParents) - 1_000_000 - 1) * 3 + 1
        

        # print(link.id_certificate_newbornParents)
        # print(father, mother)

        # groom = (int(link.id_certificate_partners) - 1) * 6 + 3
        # bride = (int(link.id_certificate_partners) - 1) * 6
        
        # print(link.id_certificate_partners)
        # print(groom, bride)

        # father = df_births.at[father, "firstname"] + df_births.at[father, "familyname"]
        # mother = df_births.at[mother, "firstname"] + df_births.at[mother, "familyname"]

        # print(father, mother)

        # groom = df_marriages.at[groom, "firstname"] + df_marriages.at[groom, "familyname"]
        # bride = df_marriages.at[bride, "firstname"] + df_marriages.at[bride, "familyname"]

        # print(groom, bride)
    #     break

    # df_clean_matches = pd.DataFrame(links_uuid, columns=["parents_id", "partners_id"])
    # df_clean_matches.to_csv("clean matches.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


def unique_individuals():
    df_links_marriages = pd.read_csv("data\\results\\links h persons.csv", sep=";")
    df_links_births = pd.read_csv("data\\results\\links b persons.csv", sep=",")

    unique_individuals = []
    unique_person_id = 0

    for link_marriage in df_links_marriages.itertuples():
        if link_marriage.parent_id in [individual[0] for individual in unique_individuals]:
            continue

        parents = df_links_marriages.loc[df_links_marriages['parent_id'] == link_marriage.parent_id]
        partners = df_links_marriages.loc[df_links_marriages['partner_id'] == link_marriage.partner_id]

        for parent in parents.itertuples():
            unique_individuals.append([parent.partner_id, unique_person_id, "partner"])

        references = set()
        for partner in partners.itertuples():
            unique_individuals.append([partner.parent_id, unique_person_id, "parent"])
            # check births
            parents_birth = df_links_births.loc[df_links_births['partners_id'] == partner.partner_id]
            for parent_birth in parents_birth.itertuples():
                references.add(parent_birth.parent_id)

        for reference in references:
            unique_individuals.append([reference, unique_person_id, "parent birth"])
    
        unique_person_id += 1

        if unique_person_id % 1000 == 0:
            print(unique_person_id)

        if unique_person_id == 100:
            break
    
    df_unique_individuals = pd.DataFrame(unique_individuals, columns=["uuid", "unique_person_id", "role"])
    df_unique_individuals.to_csv(unique_file_name("data\\unique_individuals", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


# unique_individuals()


def process_unique_timeline(uuid):
    df_unique_persons = pd.read_csv("data\\unique_individuals (4).csv", sep=";")
    df_persons_marriage = pd.read_csv("data\\Marriages\\persons.csv", sep=";")
    df_registrations_marriage = pd.read_csv("data\\Marriages\\marriages.csv", sep=";")
    df_births = pd.read_csv("data\\Births\\persons.csv", sep=";")

    unique_person_id = df_unique_persons.loc[df_unique_persons['uuid'] == uuid].iloc[0][ "unique_person_id"]

    references = df_unique_persons.loc[df_unique_persons['unique_person_id'] == unique_person_id]

    print(references)
    moments = pd.DataFrame(columns=["day", "month", "year", "type", "child", "partner", "uuid"])

    for index, reference in enumerate(references.itertuples()):
        if reference.role == "parent birth":
            person = df_births.loc[df_births['uuid'] == reference.uuid].iloc[0]

            child = df_births.iloc[person['id'] - (person['id'] % 3)]
            child_name = child["voornaam"] + " " + child["geslachtsnaam"]

            moments.loc[index, "day"] = int(child["dag"])
            moments.loc[index, "month"] = int(child["maand"])
            moments.loc[index, "year"] = int(child["jaar"])

            moments.loc[index, "type"] = "Child born"
            moments.loc[index, "child"] = child_name
            moments.loc[index, "uuid"] = reference.uuid
            continue

        person = df_persons_marriage.loc[df_persons_marriage['uuid'] == reference.uuid].iloc[0]
        registration_id = (person['id'] - (person['id'] % 6)) / 6

        moments.loc[index, "day"] = int(df_registrations_marriage.at[registration_id, "dag"])
        moments.loc[index, "month"] = int(df_registrations_marriage.at[registration_id, "maand"])
        moments.loc[index, "year"] = int(df_registrations_marriage.at[registration_id, "jaar"])

        moments.loc[index, "uuid"] = reference.uuid
        
        if reference.role == "parent":
            child_id = person['id'] - (person['id'] % 6)
            if not "bruidegom" in person["rol"]:
                child_id += 3

            child_name = df_persons_marriage.at[child_id, "voornaam"] + " " + df_persons_marriage.at[child_id, "geslachtsnaam"]

            moments.loc[index, "type"] = "Child married"
            moments.loc[index, "child"] = child_name


        elif reference.role == "partner":        
            partner_id = person['id'] - (person['id'] % 6)
            if person["rol"] == "Bruidegom":
                partner_id += 3

            partner_name = df_persons_marriage.at[partner_id, "voornaam"] + " " + df_persons_marriage.at[partner_id, "geslachtsnaam"]

            moments.loc[index, "type"] = "Married"
            moments.loc[index, "partner"] = partner_name

    moments = moments.sort_values(by=["year", "month", "day"])
    print(moments)
    

    moments.to_csv(unique_file_name("moments", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)

process_unique_timeline("462f94b1-8751-71f7-17a3-3a23a7192477")

