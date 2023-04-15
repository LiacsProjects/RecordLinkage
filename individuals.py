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

    df_person_links = pd.DataFrame(person_links, columns=["parent_id", "partner_id", "sex"])
    df_person_links.to_csv("data\\links b persons.csv", sep=",", index=False, quoting=csv.QUOTE_NONNUMERIC)


def unique_individuals_bl():
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

def get_roles(role):
    references = []
    potential_links = []
    for mode in MODES:
        if MODES[mode]["references"] == role:
            references.append(mode)

        if MODES[mode]["potential_links"] == role:
            potential_links.append(mode)
    
    return references, potential_links


def unique_individuals_rl():

    def get_references(df_links:pd.DataFrame, uuid, role, links):
        references, potential_links = get_roles(role)

        df_references = pd.concat([grouped_dfs[i] for i in modesfs])
        

        for reference in df_references[df_references["reference_uuid"].values == uuid].itertuples():
            if reference.link_uuid not in [link[0] for link in links]:
                role = MODES[reference.mode]["potential_links"]
                links.append([reference.link_uuid, role, reference.sex])
                # print("refer", reference.link_uuid)

                links = get_references(df_links, reference.link_uuid, role, links)

        df_potential_links = df_links[df_links["mode"].values == potential_links]
        for link in df_potential_links[df_potential_links["link_uuid"].values == uuid].itertuples():
            if link.reference_uuid not in [link[0] for link in links]:
                role = MODES[link.mode]["references"]
                links.append([link.reference_uuid, role, link.sex])
                # print("link", link.reference_uuid)

                links = get_references(df_links, link.reference_uuid, role, links)

        return links
            

    dfs = [pd.read_csv("results\\recordLinker\\RL Links Persons.csv", sep=";"), 
           pd.read_csv("results\\recordLinker\\RL Links Persons (1).csv", sep=";"), 
           pd.read_csv("results\\recordLinker\\RL Links Persons (2).csv", sep=";"), 
           pd.read_csv("results\\recordLinker\\RL Links Persons (3).csv", sep=";")]
    
    df_links = pd.concat(dfs)
    print(df_links)
    grouped_dfs = dict(tuple(df_links.groupby('mode')))

    print(pd.concat([grouped_dfs[i] for i in modesfs]))
    # df_links = df_links.groupby(["mode"])
    # print(df_links.get_group(1))

    return
  
    # df_links = df_links.set_index(["reference_uuid"])

    
    unique_individuals = []
    unique_person_id = 0
    for link_person in df_links[df_links["reference_uuid"] == "d96541a8-717d-6f6e-013d-99efd43705ad"].itertuples():
    # for link_person in df_links.itertuples():
        start = time.time()
        if link_person.link_uuid in [individual[0] for individual in unique_individuals]:
            continue

        MODES[link_person.mode]["potential_links"] 

        links = get_references(df_links, 
                               link_person.link_uuid, 
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
    
    df_unique_individuals = pd.DataFrame(unique_individuals, columns=["uuid", "unique_person_id", "role", "sex"])
    df_unique_individuals.to_csv(unique_file_name("unique_individuals", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


unique_individuals_rl()


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

# process_unique_timeline("462f94b1-8751-71f7-17a3-3a23a7192477")

def process_timeline():
    pass