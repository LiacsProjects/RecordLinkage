# https://stackoverflow.com/questions/57512155/how-to-draw-a-tree-more-beautifully-in-networkx

import matplotlib.pyplot as plt
import networkx as nx
import pydot
import csv
import os
from networkx.drawing.nx_pydot import graphviz_layout
import pandas as pd

# G = nx.Graph()
# G.add_node("dad")
# G.add_node("dad")

# # G.add_edge("mom", "dad")
# # G.add_edge("mom", "mom2")

# pos = graphviz_layout(G, prog="dot")
# nx.draw(G, pos)
# plt.show()


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


def generate_persons():
    df_marriage_unfiltered = pd.read_csv(r'data\unprocessed\Huwelijk.csv', sep=";", dtype="string")
    persons = []
    count = 0

    for marriage in df_marriage_unfiltered.itertuples():
        for type in ["Bruidegom", "Bruid", "Vader bruidegom", "Moeder bruidegom", "Vader bruid", "Moeder bruid"]:
            person = [
                count, 
                f"{type}-uuid",
                type, 
                f"{type}-Voornaam", 
                f"{type}-Tussenvoegsel", 
                f"{type}-Geslachtsnaam", 
                f"{type}-Leeftijd", 
                f"{type}-Beroep", 
                f"{type}-Plaats geboorte", 
                f"{type}-Datum geboorte", 
                f"{type}-Plaats wonen"]

            persons.append(person)
            count += 1




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


    for match in df_matches.itertuples():

        for type in




        marriage = df_marriage.loc[df_marriage['uuid'] == parent.partners_id].iloc[0]

        persons = []
        for type in ["Bruidegom", "Bruid", "Vader bruidegom", "Moeder bruidegom", "Vader bruid", "Moeder bruid"]:

            




            name = " ". join([str(marriage[f"{type}-Voornaam"]).replace("<NA>", ""), str(marriage[f"{type}-Tussenvoegsel"]).replace("<NA>", ""), str(marriage[f"{type}-Geslachtsnaam"]).replace("<NA>", "")])
            persons.append([name, type])












































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


get_family()







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

