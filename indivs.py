import Levenshtein
import csv
import os
import pandas as pd
import time



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


def get_roles(role):
    references = []
    potential_links = []
    for mode in MODES:
        if MODES[mode]["references"] == role:
            references.append(mode)

        if MODES[mode]["potential_links"] == role:
            potential_links.append(mode)
    if references == []:
        print(role)
    return references, potential_links


def unique_individuals_rl():

    dfs = [pd.read_csv("results\\recordLinker\\RL Links Persons.csv", sep=";"), 
           pd.read_csv("results\\recordLinker\\RL Links Persons (1).csv", sep=";"), 
           pd.read_csv("results\\recordLinker\\RL Links Persons (2).csv", sep=";"), 
           pd.read_csv("results\\recordLinker\\RL Links Persons (3).csv", sep=";")]
    
    df_links = pd.concat(dfs)
    print(df_links)
    grouped_dfs = dict(tuple(df_links.groupby('mode')))


    def get_references(uuid, role, links):
        modes_references, modes_links = get_roles(role)
        print(modes_references, modes_links)

        df_references = pd.concat([grouped_dfs[mode] for mode in modes_references])
        for reference in df_references[df_references["reference_uuid"].values == uuid].itertuples():
            if reference.link_uuid in [link[0] for link in links]:
                continue

            role = MODES[reference.mode]["potential_links"]
            links.append([reference.link_uuid, role, reference.sex])
            print("refer", reference.link_uuid)

            links = get_references(reference.link_uuid, role, links)
        if len(modes_links) == 0:
            return links
        
        df_potential_links = pd.concat([grouped_dfs[mode] for mode in modes_links])
        for link in df_potential_links[df_potential_links["link_uuid"].values == uuid].itertuples():
            if link.reference_uuid in [link[0] for link in links]:
                continue

            role = MODES[link.mode]["references"]
            links.append([link.reference_uuid, role, link.sex])
            print("link", link.reference_uuid)

            links = get_references(link.reference_uuid, role, links)

        return links

    
    unique_individuals = []
    unique_person_id = 0
    for link_person in df_links[df_links["reference_uuid"] == "d96541a8-717d-6f6e-013d-99efd43705ad"].itertuples():
    # for link_person in df_links.itertuples():
        if link_person.link_uuid in [individual[0] for individual in unique_individuals]:
            continue

        print(link_person)
        start = time.time()

        links = get_references(link_person.link_uuid, 
                               MODES[link_person.mode]["potential_links"], 
                               [[link_person.link_uuid, MODES[link_person.mode]["potential_links"], link_person.sex]])

        for link in links:
            uuid = link[0]
            role = link[1]
            sex = link[2]
            unique_individuals.append([uuid, unique_person_id, role, sex])

        unique_person_id += 1

        if unique_person_id % 10 == 0:
            print(unique_person_id)

        if unique_person_id == 100:
            break
        print(time.time() - start)
        break
    
    df_unique_individuals = pd.DataFrame(unique_individuals, columns=["uuid", "unique_person_id", "role", "sex"])
    df_unique_individuals.to_csv(unique_file_name("unique_individuals", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


unique_individuals_rl()