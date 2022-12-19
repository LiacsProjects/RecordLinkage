import matplotlib.pyplot as plt
import networkx as nx
import csv
import os
from networkx.drawing.nx_pydot import graphviz_layout
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


def get_tree():
    df_matches = pd.read_csv("clean matches.csv", sep=";")
    # df_marriage = pd.read_csv(r'data\processed\huwelijk.csv', dtype="string")

    G = nx.Graph()


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
        parents = df_matches.loc[df_matches["parents_id"] == cert]

        for parent in parents.itertuples():

            G.add_node(parent.partners_id)
            G.add_edge(cert, parent.partners_id)

            # marriage = df_marriage.loc[df_marriage['uuid'] == parent.partners_id].iloc[0]

            # persons = []
            # for type in ["Bruidegom", "Bruid", "Vader bruidegom", "Moeder bruidegom", "Vader bruid", "Moeder bruid"]:
            #     name = " ". join([str(marriage[f"{type}-Voornaam"]).replace("<NA>", ""), str(marriage[f"{type}-Tussenvoegsel"]).replace("<NA>", ""), str(marriage[f"{type}-Geslachtsnaam"]).replace("<NA>", "")])
            #     persons.append([name, type])

            find_recursive_parents(parent.partners_id)


    print("Constructing graph")
    for match in df_matches.itertuples():
        G.add_node(match.partners_id)
        G.add_node(match.parents_id)
        G.add_edge(match.parents_id, match.partners_id)

        youngest = find_recursive_child(match, 0)

        G.add_node(youngest[0].parents_id)

        find_recursive_parents(youngest[0].parents_id)

        break
    
    print("Generating positions")

    pos = graphviz_layout(G, prog="twopi")
    # pos = graphviz_layout(G, prog="dot")
    # pos = nx.spring_layout(G)
    
    print("Drawing graph")
    nx.draw(G, pos)

    file = unique_file_name("trees\\Partial tree", FORMAT)
    print(f"Saving \"{file}\"\n")
    plt.savefig(file, format=FORMAT, dpi=DPI)


def get_tree_all():
    df_matches = pd.read_csv("clean matches.csv", sep=";")

    fig = plt.figure(figsize=(40,40))
    G = nx.Graph()

    print("Constructing graph")
    for match in df_matches.itertuples():

        G.add_node(match.partners_id)
        G.add_node(match.parents_id)
        G.add_edge(match.parents_id, match.partners_id)

        if G.number_of_nodes() > 10000:
            break
    
    print("Generating positions")

    pos = graphviz_layout(G, prog="twopi")
    # pos = graphviz_layout(G, prog="dot")
    # pos = nx.spring_layout(G)
    
    print("Drawing graph")
    nx.draw(G, pos, node_size=50)
    # nx.drawing.nx_pydot.write_dot(G,path)
    file = unique_file_name("trees\\Complete tree", FORMAT)
    print(f"Saving \"{file}\"\n")
    fig.savefig(file, format=FORMAT, dpi=DPI)


# get_tree()
get_tree_all()

