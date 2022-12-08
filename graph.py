# https://stackoverflow.com/questions/57512155/how-to-draw-a-tree-more-beautifully-in-networkx

import matplotlib.pyplot as plt
import networkx as nx
import pydot
import csv
from networkx.drawing.nx_pydot import graphviz_layout
import pandas as pd

# G = nx.Graph()
# # G.add_node("dad")

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
    # return matches




def get_family():
    df_matches = pd.read_csv("clean matches.csv", sep=";")
    # df_marriage = pd.read_csv(r'data\processed\huwelijk.csv', dtype="string")
    
    def find_recursive_child(match, depth):
        children = df_matches.loc[df_matches["parents_id"] == match.partners_id]
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


    # G = nx.Graph()
    max_depth = 0
    for match in df_matches.itertuples():
        # marriage_parents = df_marriage.loc[df_marriage['uuid'] == match.parents_id].iloc[0] 
        # marriage_partners = df_marriage.loc[df_marriage['uuid'] == match.partners_id].iloc[0]
        print(match)

        old = find_recursive_child(match, 0)
        # match 
        print(old)


        # for match in df_matches.loc[df_matches["parents_id"] == match.partners_id].itertuples():
        #     for 


        # print(marriage_parents, "\n", marriage_partners)
        break

    # pos = graphviz_layout(G, prog="dot")
    # nx.draw(G, pos)
    # plt.show()


# read_matches()
# print("read matches")

get_family()

