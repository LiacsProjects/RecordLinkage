# https://stackoverflow.com/questions/57512155/how-to-draw-a-tree-more-beautifully-in-networkx

import matplotlib.pyplot as plt
import networkx as nx
import pydot
import Levenshtein
import csv
import os
from networkx.drawing.nx_pydot import graphviz_layout
import pandas as pd


INDEX_GROOM = 30
INDEX_GROOM_FATHER = 48
INDEX_GROOM_MOTHER = 66
INDEX_BRIDE = 84
INDEX_BRIDE_FATHER = 102
INDEX_BRIDE_MOTHER = 120

FORMAT = "svg"
DPI = 300


def unique_file_name(path, extension = ""):
    i = 0
    temp_path = path
    while os.path.exists(temp_path + "." + extension):  #check of het bestand al bestaat
        i += 1
        temp_path = path + " ({})".format(str(i))
    return temp_path + "." + extension


def match_certificates():
    df_matches = pd.read_csv("matches.csv", sep=";")
    id_map = pd.read_csv("registrations.csv", sep=";")

    matches = []
    for row in df_matches.itertuples():
        id_certificate_parents = id_map.loc[id_map['id_registration'] == row.id_certificate_parents].iloc[0]['registration_seq']
        id_certificate_partners = id_map.loc[id_map['id_registration'] == row.id_certificate_partners].iloc[0]['registration_seq']

        # print(id_certificate_parents, id_certificate_partners)
        matches.append([id_certificate_parents, id_certificate_partners])
        # break
    
    df_clean_matches = pd.DataFrame(matches, columns=["parents_id", "partners_id"])
    df_clean_matches.to_csv("clean matches.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


def clean(value):
    return str(value).replace("<NA>", "").strip()


def generate_persons():

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
    persons = []
    marriages = []
    person_id = 0

    for marriage_unfiltered in df_marriage_unfiltered.itertuples():
        day, month, year = get_date(marriage_unfiltered[27])

        marriage = [
            marriage_unfiltered[0],                     # id
            marriage_unfiltered[1],                     # uuid
            day, month, year,                           # Date
            marriage_unfiltered[INDEX_GROOM],           # Bruidegom uuid
            marriage_unfiltered[INDEX_GROOM_FATHER],    # Vader bruidegom uuid
            marriage_unfiltered[INDEX_GROOM_MOTHER],    # Moeder bruidegom uuid
            marriage_unfiltered[INDEX_BRIDE],           # Bruid uuid
            marriage_unfiltered[INDEX_BRIDE_FATHER],    # Vader bruid uuid
            marriage_unfiltered[INDEX_BRIDE_MOTHER]]    # Moeder bruid uuid

        marriages.append(marriage)
    
        for role in ["Bruidegom", "Vader bruidegom", "Moeder bruidegom", "Bruid", "Vader bruid", "Moeder bruid"]:
            index = get_index(role)
            birth_day, birth_month, birth_year = get_date(clean(marriage_unfiltered[index + 15]))

            person = [
                person_id,                                          # id
                marriage_unfiltered[index],                         # uuid
                role,                                               # Role
                clean(marriage_unfiltered[index + 9]),              # Voornaam
                clean(marriage_unfiltered[index + 10]),             # Tussenvoegsel
                clean(marriage_unfiltered[index + 11]),             # Geslachtsnaam
                get_age(clean(marriage_unfiltered[index + 12])),    # Age
                clean(marriage_unfiltered[index + 13]),             # Beroep
                clean(marriage_unfiltered[index + 14]),             # Geboorte plaats
                birth_day, birth_month, birth_year,                 # Geboorte datum
                clean(marriage_unfiltered[index + 16])]             # Woonplaats
            
            persons.append(person)
            person_id += 1


    df_marriage = pd.DataFrame(marriages, columns=[
        "id", 
        "uuid", 
        "dag", 
        "maand", 
        "jaar", 
        "bruidegom_uuid", 
        "vader_bruidegom_uuid", 
        "moeder_bruidegom_uuid", 
        "bruid_uuid", 
        "vader_bruid_uuid", 
        "moeder_bruid_uuid"])

    df_persons = pd.DataFrame(persons, columns=[
        "id", 
        "uuid", 
        "rol", 
        "voornaam", 
        "tussenvoegsel", 
        "geslachtsnaam", 
        "leeftijd", 
        "beroep", 
        "geboorteplaats", 
        "dag",
        "maand", 
        "jaar", 
        "woonplaats"])

    df_marriage.to_csv("marriages.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
    df_persons.to_csv("persons.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


def construct_person_links():
    df_marriages = pd.read_csv("marriages.csv", sep=";", dtype="string")
    df_persons = pd.read_csv("persons.csv", sep=";", dtype="string")
    df_matches = pd.read_csv("clean matches.csv", sep=";")
    G = nx.Graph()

    def get_name(uuid, role):
        person = df_persons.loc[(df_persons["uuid"] == uuid) & (df_persons["rol"] == role)].iloc[0]
        name = " ".join(" ".join([clean(person["voornaam"]), clean(person["tussenvoegsel"]), clean(person["geslachtsnaam"])]).split())
        print(name, role)
        return name
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

        print()
        print()

        if Levenshtein.distance(partners_string, groom_parents_string) < Levenshtein.distance(partners_string, bride_parents_string):
            links.append([parents[0], partners[0] , "m"])
            links.append([parents[1], partners[1], "v"])
        else:
            links.append([parents[2], partners[0], "m"])
            links.append([parents[3], partners[1], "v"])

        print(links)
        # for partner in partners:
        #     get_name(partner)
        #     break

        # for certificate in match[1:]:
        #     marriage = df_marriages.loc[df_marriages["uuid"] == str(certificate)].iloc[0]
        #     ids.append(list(marriage[5:]))


        #     links.append([
        #         [marriage["vader_bruidegom_uuid"], marriage["bruidegom_uuid"], "vader"],
        #         [marriage["moeder_bruidegom_uuid"], marriage["bruidegom_uuid"], "moeder"],
        #         # [marriage["bruidegom_uuid"], marriage["bruid_uuid"], "partner"],
        #         [marriage["vader_bruid_uuid"], marriage["bruid_uuid"], "vader"],
        #         [marriage["moeder_bruid_uuid"], marriage["bruid_uuid"], "moeder"],
        #     ])

            # G.add_edge(marriage["vader_bruidegom_uuid"], marriage["bruidegom_uuid"])
            # G.add_edge(marriage["moeder_bruidegom_uuid"], marriage["bruidegom_uuid"])
            # G.add_edge(marriage["vader_bruid_uuid"], marriage["bruid_uuid"])
            # G.add_edge(marriage["moeder_bruid_uuid"], marriage["bruid_uuid"])

            # G.add_edge(marriage["bruidegom_uuid"], "testkind")
            # G.add_edge(marriage["bruid_uuid"], "testkind")


            # break
            # links.append([])

        # parent -> 
        # print(ids)
        # for id in ids:



        # pos = graphviz_layout(G, prog="dot")
        # nx.draw(G, pos, node_size=50)

        # file = unique_file_name("test trees\\Test tree", FORMAT)
        # print(f"Saving \"{file}\"\n")
        # plt.savefig(file, format=FORMAT, dpi=DPI)

        break


    



construct_person_links()







def test():
    df_marriage_unfiltered = pd.read_csv(r'data\unprocessed\Huwelijk.csv', sep=";", dtype="string")
    df_matches = pd.read_csv("clean matches.csv", sep=";")

    df_marriage = df_marriage_unfiltered[["uuid", 
        "Bruidegom-uuid", "Bruidegom-Voornaam", "Bruidegom-Tussenvoegsel", "Bruidegom-Geslachtsnaam", 
        "Vader bruidegom-uuid", "Vader bruidegom-Voornaam", "Vader bruidegom-Tussenvoegsel", "Vader bruidegom-Geslachtsnaam",
        "Moeder bruidegom-uuid", "Moeder bruidegom-Voornaam", "Moeder bruidegom-Tussenvoegsel", "Moeder bruidegom-Geslachtsnaam",
        "Bruid-uuid", "Bruid-Voornaam", "Bruid-Tussenvoegsel", "Bruid-Geslachtsnaam", 
        "Vader bruid-uuid", "Vader bruid-Voornaam", "Vader bruid-Tussenvoegsel", "Vader bruid-Geslachtsnaam", 
        "Moeder bruid-uuid", "Moeder bruid-Voornaam", "Moeder bruid-Tussenvoegsel", "Moeder bruid-Geslachtsnaam"]]


    # for match in df_matches.itertuples():

    #     for type in




    #     marriage = df_marriage.loc[df_marriage['uuid'] == parent.partners_id].iloc[0]

    #     persons = []
    #     for type in ["Bruidegom", "Bruid", "Vader bruidegom", "Moeder bruidegom", "Vader bruid", "Moeder bruid"]:

            




    #         name = " ". join([str(marriage[f"{type}-Voornaam"]).replace("<NA>", ""), str(marriage[f"{type}-Tussenvoegsel"]).replace("<NA>", ""), str(marriage[f"{type}-Geslachtsnaam"]).replace("<NA>", "")])
    #         persons.append([name, type])












































def unique_file_name(path, extension = ""):
    i = 0
    temp_path = path
    while os.path.exists(temp_path + extension):  #check of het bestand al bestaat
        i += 1
        temp_path = path + " ({})".format(str(i))
    return temp_path + extension


def read_matches():
    df_matches = pd.read_csv("matches.csv", sep=";")
    id_map = pd.read_csv("registrations.csv", sep=";")

    matches = []
    for row in df_matches.itertuples():
        id_certificate_parents = id_map.loc[id_map['id_registration'] == row.id_certificate_parents].iloc[0]['registration_seq']
        id_certificate_partners = id_map.loc[id_map['id_registration'] == row.id_certificate_partners].iloc[0]['registration_seq']

        # print(id_certificate_parents, id_certificate_partners)
        matches.append([id_certificate_parents, id_certificate_partners])
        # break
    
    df_clean_matches = pd.DataFrame(matches, columns=["parents_id", "partners_id"])
    df_clean_matches.to_csv("clean matches.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
    # return matches




def get_family():
    df_matches = pd.read_csv("clean matches.csv", sep=";")
    df_marriage = pd.read_csv(r'data\processed\huwelijk.csv', dtype="string")

    fig = plt.figure(figsize=(40,40))
    G = nx.Graph()

    added = []


    def find_recursive_child(match, depth):
        children = df_matches.loc[df_matches["partners_id"] == match.parents_id]
        if len(children) > 0:
            depths = []
            childs = []
            for child in children.itertuples():
                res = find_recursive_child(child, depth + 1)
                childs.append(res[0])
                depths.append(res[1])

            return childs[depths.index(max(depths))], max(depths)
        else:
            return match, depth


    def find_recursive_parents(cert):
        added.append(cert)
        parents = df_matches.loc[df_matches["parents_id"] == cert]
        # print("\n", len(parents))

        for parent in parents.itertuples():

            G.add_node(parent.partners_id)
            G.add_edge(cert, parent.partners_id)

            marriage = df_marriage.loc[df_marriage['uuid'] == parent.partners_id].iloc[0]

            persons = []
            for type in ["Bruidegom", "Bruid", "Vader bruidegom", "Moeder bruidegom", "Vader bruid", "Moeder bruid"]:
                name = " ". join([str(marriage[f"{type}-Voornaam"]).replace("<NA>", ""), str(marriage[f"{type}-Tussenvoegsel"]).replace("<NA>", ""), str(marriage[f"{type}-Geslachtsnaam"]).replace("<NA>", "")])
                persons.append([name, type])

            # print(parents['uuid'])
            # print(marriage['Jaar'], marriage['uuid'])
            # print(persons)

            find_recursive_parents(marriage['uuid'])

    print("Constructing graph")
    for match in df_matches.itertuples():
        # if match.parents_id in added:
            # print("already added")
            # continue

        G.add_node(match.partners_id)
        G.add_node(match.parents_id)
        G.add_edge(match.parents_id, match.partners_id)

        # marriage_parents = df_marriage.loc[df_marriage['uuid'] == match.parents_id].iloc[0] 
        # marriage_partners = df_marriage.loc[df_marriage['uuid'] == match.partners_id].iloc[0]
        # print("Start:", match)

        # youngest = find_recursive_child(match, 0)
        # match 
        # print("Youngest:", old)
        # print("Parents:", old[0].parents_id)
        # print("Partners:", old[0].partners_id)

        # parents = df_matches.loc[df_matches["parents_id"] == old[0].parents_id]

        # marriage = df_marriage.loc[df_marriage['uuid'] == youngest[0].parents_id].iloc[0]

        # persons = []
        # for type in ["Bruidegom", "Bruid", "Vader bruidegom", "Moeder bruidegom", "Vader bruid", "Moeder bruid"]:
        #     name = " ". join([str(marriage[f"{type}-Voornaam"]).replace("<NA>", ""), str(marriage[f"{type}-Tussenvoegsel"]).replace("<NA>", ""), str(marriage[f"{type}-Geslachtsnaam"]).replace("<NA>", "")])
        #     persons.append([name, type])

        # print(marriage['uuid'])
        # print(marriage['Jaar'])
        # print(persons)

        # G.add_node(youngest[0].parents_id)

        # find_recursive_parents(youngest[0].parents_id)
        # if len(added) > 1000:
        #     break
        # break
        if G.number_of_nodes() > 1000:
            break
    
    print("Generating positions")
    node_size = 10
    dpi = 300
    format = "svg"

    pos = graphviz_layout(G, prog="twopi")
    # pos = graphviz_layout(G, prog="dot")
    # pos = nx.spring_layout(G)
    
    print("Drawing graph")
    nx.draw(G, pos, node_size=node_size)

    file = unique_file_name("trees\\tree " + str(node_size), "." + format)
    print(f"Saving \"{file}\"")
    fig.savefig(file, format=format, dpi=dpi)


# get_family()







        # parents = df_marriage.loc[df_marriage['uuid'] == old[0].partners_id].iloc[0]

        # persons = []
        # for type in ["Bruidegom", "Bruid", "Vader bruidegom", "Moeder bruidegom", "Vader bruid", "Moeder bruid"]:
        #     name = " ". join([str(parents[f"{type}-Voornaam"]).replace("<NA>", ""), str(parents[f"{type}-Tussenvoegsel"]).replace("<NA>", ""), str(parents[f"{type}-Geslachtsnaam"]).replace("<NA>", "")])
        #     persons.append([name, type])

        # print(parents['uuid'])
        # print(parents['Jaar'])
        # print(persons)

        

            # parents = df_matches.loc[df_matches["parents_id"] == old[0].parents_id]



        #     # marriage_bride = df_marriage.loc[df_marriage['uuid'] == match.partners_id].iloc[0]

        #     persons = []
        #     for type in ["Bruidegom", "Bruid", "Vader bruidegom", "Moeder bruidegom", "Vader bruid", "Moeder bruid"]:
        #         name = " ". join([str(parent[f"{type}-Voornaam"]).replace("<NA>", ""), str(parent[f"{type}-Tussenvoegsel"]).replace("<NA>", ""), str(parent[f"{type}-Geslachtsnaam"]).replace("<NA>", "")])
        #         persons.append([name, type])

        #     print(parent['uuid'])
        #     print(parent['Jaar'])
        #     print(persons)
        #     break




        # for match in df_matches.loc[df_matches["parents_id"] == match.partners_id].itertuples():
        #     for 


        # print(marriage_parents, "\n", marriage_partners)
    # pos = graphviz_layout(G, prog="dot")
    # nx.draw(G, pos)
    # plt.show()


# read_matches()
# print("read matches")

