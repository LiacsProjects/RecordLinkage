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
    df_matches = pd.read_csv("data\\clean matches.csv", sep=";")

    checked_certificates = []
    family_graph_max = nx.Graph()


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
            checked_certificates.append(parent.partners_id)
            family_graph.add_node(parent.partners_id)
            family_graph.add_edge(cert, parent.partners_id)

            find_recursive_parents(parent.partners_id)


    print("Constructing graph")
    for match in df_matches.itertuples():
        if match[0] == 10000:
            print(match[0])
            break

        if match.parents_id in checked_certificates:
            continue

        family_graph = nx.Graph()

        youngest = find_recursive_child(match, 0)

        checked_certificates.append(youngest[0].parents_id)
        family_graph.add_node(youngest[0].parents_id)

        find_recursive_parents(youngest[0].parents_id)

        if family_graph.number_of_nodes() > family_graph_max.number_of_nodes():
            family_graph_max = family_graph
        # break
    
    print("Generating positions")

    # pos = graphviz_layout(G, prog="twopi")
    pos = graphviz_layout(family_graph_max, prog="dot")
    # pos = nx.spring_layout(G)
    
    print("Drawing graph")
    nx.draw(family_graph_max, pos)

    file = unique_file_name("trees\\Partial tree", FORMAT)
    print(f"Saving \"{file}\"\n")
    plt.savefig(file, format=FORMAT, dpi=DPI)


def get_tree_all(layout, size):
    df_matches = pd.read_csv("data\\clean matches.csv", sep=";")

    fig = plt.figure(figsize=(40,40))
    G = nx.Graph()

    print("Constructing graph")
    for match in df_matches.itertuples():

        G.add_node(match.partners_id)
        G.add_node(match.parents_id)
        G.add_edge(match.parents_id, match.partners_id)

        if G.number_of_nodes() > size:
            break
    
    print("Generating positions")
    if layout == "spring":
        pos = nx.spring_layout(G)
    else:
        pos = graphviz_layout(G, prog=layout)
    
    print("Drawing graph")
    nx.draw(G, pos, node_size=50)
    # nx.drawing.nx_pydot.write_dot(G,path)
    file = unique_file_name(f"trees\\Complete tree {layout} {str(size)}", FORMAT)
    print(f"Saving \"{file}\"\n")
    fig.savefig(file, format=FORMAT, dpi=DPI)


# get_tree()

layout = "twopi"
# layout = "dot"
# layout = "neato"
# layout = "spring"
size = 30000
# get_tree_all(layout, size)


def get_tree_individuals():
    df_relations = pd.read_csv("data\\relations.csv", sep=";")
    df_links = pd.read_csv("data\\links.csv", sep=";")

    # def find_relations(graph, id):
    #     if relation.role1 == "zoon":
    #         family_node_color_map.append('blue')
    #     else:
    #         family_node_color_map.append('purple')
    #     graph.add_node(relation.rel1_id)

    #     df_rels = df_relations.loc[df_relations["rel1_id"] == id]
    #     for rel in df_rels.iterrows():
    #         graph.add_edge(relation.rel1_id, relation.rel2_id, color='black')


    for relation in df_relations.itertuples():
        if relation.Index < 39693:
            continue
        family_graph = nx.Graph()
        family_node_color_map = []


        """
        Doe dat je een uuid geeft, en dat daaruit dan de grafiek gemaakt wordt
        
        """
        if relation.role1 == "zoon":
            family_node_color_map.append('blue')
        else:
            family_node_color_map.append('purple')
        family_graph.add_node(relation.rel1_id)

        if relation.role2 == "vader":
            family_node_color_map.append('blue')
        else:
            family_node_color_map.append('purple')
        family_graph.add_node(relation.rel2_id)

        family_graph.add_edge(relation.rel1_id, relation.rel2_id, color='black')

        print(relation)
        if df_relations.at[relation.Index + 1, "rel1_id"] == relation.rel1_id:
            other_rel = df_relations.at[relation.Index + 1, "rel2_id"]
            if df_relations.at[relation.Index + 1, "role2"] == "vader":
                family_node_color_map.append('blue')
            else:
                family_node_color_map.append('purple')
            family_graph.add_node(other_rel)
            family_graph.add_edge(relation.rel1_id, other_rel, color='black')

        df_match = df_links.loc[df_links["partner_id"] == relation.rel1_id]
        print(df_match)

        
        pos = graphviz_layout(family_graph, prog="dot")
        # pos = nx.spring_layout(G)
        
        print("Drawing graph")
        nx.draw(family_graph, pos, node_color=family_node_color_map)

        file = unique_file_name("trees\\Partial tree individual", FORMAT)
        print(f"Saving \"{file}\"\n")
        plt.savefig(file, format=FORMAT, dpi=DPI)
        break






get_tree_individuals()

