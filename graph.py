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


def get_tree_individuals(uuid):
    df_relations = pd.read_csv("data\\relations.csv", sep=";")
    df_links = pd.read_csv("data\\links.csv", sep=";")

    family_graph = nx.Graph()


    def find_relations(uuid):
        relations = []
        partner = ""

        df_rels = df_relations.loc[df_relations["rel1_id"] == uuid]
        for rel in df_rels.itertuples():
            if rel.rel_type == "partner":
                partner = rel.rel2_id

            relations.append(rel)

        df_rels = df_relations.loc[df_relations["rel2_id"] == uuid]
        for rel in df_rels.itertuples():
            if rel.rel_type == "partner" and rel.rel1_id != uuid:
                partner = rel.rel1_id

            relations.append(rel)

        df_rels = df_relations.loc[df_relations["rel1_id"] == partner]
        for rel in df_rels.itertuples():
            if rel.rel_type != "partner":
                relations.append(rel)

        return relations


    def add_node(uuid, sex):
        if uuid not in family_graph:
            if sex == "m":
                color = "blue"
            elif sex == "v":
                color = "purple"
            else:
                color = "red"
            family_graph.add_node(uuid, color=color, value=0)


    def recurions(uuid, depth):
        for relation in find_relations(uuid):
            add_node(relation.rel1_id, relation.rel1_sex)
            add_node(relation.rel2_id, relation.rel2_sex)

            color = "black"
            if relation.rel_type == "partner":
                color = "green"

            family_graph.add_edge(relation.rel1_id, relation.rel2_id, color=color)

            if relation.rel_type != "partner":
                links = df_links.loc[df_links["parent_id"] == relation.rel2_id]

                for link in links.itertuples():
                    add_node(link.partner_id, link.sex)
                    family_graph.add_edge(relation.rel2_id, link.partner_id, color='red')
                    recurions(link.partner_id, depth + 1)


    add_node(uuid, "d")

    recurions(uuid, 0)

    edge_color_map = [family_graph[u][v]['color'] for u,v in family_graph.edges()]
    # node_color_map = [family_graph[n]['color'] for n in family_graph.nodes()]

    print(family_graph)

    node_color_map = nx.get_node_attributes(family_graph, 'color').values()

    # pos = graphviz_layout(family_graph, prog="dot")
    # pos = nx.spring_layout(family_graph)
    pos = graphviz_layout(family_graph, prog="twopi")
    
    print("Drawing graph")
    try:
        nx.draw(family_graph, pos, node_color=node_color_map, edge_color=edge_color_map, node_size=50)
    except:
        print("Drawing failed!")
        nx.draw(family_graph, pos, edge_color=edge_color_map, node_size=50)

    file = unique_file_name("trees\\Partial tree individual", FORMAT)
    nx.drawing.nx_pydot.write_dot(family_graph, unique_file_name("trees\\Partial tree individual", "dot"))
    print(f"Saving \"{file}\"\n")
    plt.savefig(file, format=FORMAT, dpi=DPI)



    #     if relation.role1 == "zoon":
    #         family_node_color_map.append('blue')
    #     else:
    #         family_node_color_map.append('purple')
    #     graph.add_node(relation.rel1_id)

    #     df_rels = df_relations.loc[df_relations["rel1_id"] == id]
    #     for rel in df_rels.iterrows():
    #         graph.add_edge(relation.rel1_id, relation.rel2_id, color='black')

    

    # links = df_links.loc[df_links["partner_id"] == uuid]
    # print("Length:", len(links.index))
    # if len(links.index) == 0:
    #     links = df_links.loc[df_links["parents_id"] == uuid]
    # rels = df_relations.loc[df_relations["rel1_id"] == uuid].reset_index(drop=True)
    # rel_nr = 1
    # if len(rels.index) == 0:
    #     rels = df_relations.loc[df_relations["rel2_id"] == uuid].reset_index(drop=True)
    #     rel_nr = 2

    # print("Rel nr:", rel_nr)

    # if rels.at[0, f'sex{rel_nr}'] == "m":
    #     family_graph.add_node(uuid, color='blue')
    # else:
    #     family_graph.add_node(uuid, color='purple')

    # for rel in rels.itertuples():
    #     if rel_nr == 1: 
    #         if rel.role2 == "m":
    #             family_graph.add_node(rel.rel2_id, color='blue')
    #         else:
    #             family_graph.add_node(rel.rel2_id, color='purple')
    #     else:
    #         if rel.role1 == "m":
    #             family_graph.add_node(rel.rel1_id, color='blue')   
    #         else:
    #             family_graph.add_node(rel.rel1_id, color='purple') 

    #     family_graph.add_edge(rel.rel1_id, rel.rel2_id, color='black')
    
    # for node in family_graph.nodes():
    #     print(node)
    # print([family_graph[n] for n in family_graph.nodes()])




    # uuid
#     find matches
#       -> ids same person
# 
# for
#   find rels
#    -> col 1
#    -> col 2
#       
#       for
#         matches
#          redo
# 


# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 
# 











    # for relation in df_relations.itertuples():
    #     if relation.Index < 39693:
    #         continue
    #     family_graph = nx.Graph()
    #     family_node_color_map = []


    #     """
    #     Doe dat je een uuid geeft, en dat daaruit dan de grafiek gemaakt wordt
        
    #     """
    #     if relation.role1 == "zoon":
    #         family_node_color_map.append('blue')
    #     else:
    #         family_node_color_map.append('purple')
    #     family_graph.add_node(relation.rel1_id)

    #     if relation.role2 == "vader":
    #         family_node_color_map.append('blue')
    #     else:
    #         family_node_color_map.append('purple')
    #     family_graph.add_node(relation.rel2_id)

    #     family_graph.add_edge(relation.rel1_id, relation.rel2_id, color='black')

    #     print(relation)
    #     if df_relations.at[relation.Index + 1, "rel1_id"] == relation.rel1_id:
    #         other_rel = df_relations.at[relation.Index + 1, "rel2_id"]
    #         if df_relations.at[relation.Index + 1, "role2"] == "vader":
    #             family_node_color_map.append('blue')
    #         else:
    #             family_node_color_map.append('purple')
    #         family_graph.add_node(other_rel)
    #         family_graph.add_edge(relation.rel1_id, other_rel, color='black')

    #     df_match = df_links.loc[df_links["partner_id"] == relation.rel1_id]
    #     print(df_match)

        

    #     break






get_tree_individuals("58ca5c18-c370-7137-5177-bab49e958ff0")

