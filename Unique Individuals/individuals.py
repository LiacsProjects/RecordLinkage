import csv
import os
import pandas as pd


def unique_file_name(path, extension = ""):
    i = 0
    temp_path = path
    while os.path.exists(temp_path + "." + extension):  #check of het bestand al bestaat
        i += 1
        temp_path = path + " ({})".format(str(i))
    return temp_path + "." + extension


def unique_individuals(linker):
    class UnionFind:
        def __init__(self, nodes):
            self.parent = {node: node for node in nodes}

        def find(self, node):
            if self.parent[node] != node:
                self.parent[node] = self.find(self.parent[node])
            return self.parent[node]

        def union(self, node1, node2):
            root1 = self.find(node1)
            root2 = self.find(node2)
            if root1 != root2:
                self.parent[root2] = root1


    def connected_nodes(edges):
        nodes = set()
        for edge in edges:
            nodes.update(edge)

        print("Nodes:", len(nodes))
        uf = UnionFind(nodes)

        for edge in edges:
            uf.union(*edge)

        groups = {}
        for node in nodes:
            root = uf.find(node)
            if root not in groups:
                groups[root] = []
            groups[root].append(node)

        return list(groups.values())


    def get_edges(linker):
        if linker == "RL":
            dfs = [pd.read_csv("RecordLinker\\results\\RL Links Persons.csv", sep=";"), 
                pd.read_csv("RecordLinker\\results\\RL Links Persons (1).csv", sep=";"), 
                pd.read_csv("RecordLinker\\results\\RL Links Persons (2).csv", sep=";")]
        elif linker == "BL":
            dfs = [pd.read_csv("BurgerLinker\\results\\BL Links Persons.csv", sep=";"), 
                pd.read_csv("BurgerLinker\\results\\BL Links Persons (1).csv", sep=";")]
            
        df_links = pd.concat(dfs).reset_index(drop=True)

        edges = []
        for link_person in df_links.itertuples():
            edges.append((link_person.reference_uuid, link_person.link_uuid))
        
        return edges


    def save_unique_individuals(unique_individuals):
        df_unique_individuals = pd.DataFrame(unique_individuals, columns=["uuid", "unique_person_id"])
        df_unique_individuals.to_csv(unique_file_name(f"Unique Individuals\\results\\{linker} Unique Individuals", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


    def save_groups(groups):
        with open(unique_file_name(f"Unique Individuals\\results\\{linker} Groups", "txt"), 'w') as f:
            for group in groups:
                f.write(','.join(str(uuid) for uuid in group) + '\n')

    edges = get_edges(linker)
    print("Edges:", len(edges))
    groups = connected_nodes(edges)
    print("Groups:", len(groups))

    # identifier = 0
    # unique_individuals = []

    # for group in groups:
    #     for node in group:
    #         unique_individuals.append([node, identifier])
    #     identifier += 1
    
    # save_unique_individuals(unique_individuals)
    # save_groups(groups)

# unique_individuals("RL")
unique_individuals("BL")

