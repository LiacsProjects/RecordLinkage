import polars as pl


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


def vind_verbonen_knopen(randen: list[tuple]):
    knopen = set()
    for rand in randen:
        knopen.update(rand)

    print("Nodes:", len(knopen))
    uf = UnionFind(knopen)

    for rand in randen:
        uf.union(*rand)

    groepen = {}
    for node in knopen:
        root = uf.find(node)
        if root not in groepen:
            groepen[root] = []
        groepen[root].append(node)

    return list(groepen.values())


def haal_op_randen():
    randen = []
    with open("links.txt", "r") as links:
        for link in links:
            randen.append(tuple(link.strip().split(";")))
    return randen


def sla_op_personen(unique_individuals):
    df_unique_individuals = pl.DataFrame(
        unique_individuals,
        orient="row",
        schema=["uuid", "unique_person_id"])
    df_unique_individuals.write_parquet("data\\resultaat\\personen.pq")


def sla_op_groepen(groepen: list):
    with open("data\\resultaat\\groepen.txt", 'w') as resultaat:
        for groep in groepen:
            resultaat.write(','.join(str(uuid) for uuid in groep) + '\n')


def maak_unieke_personen():
    randen = haal_op_randen()
    print("Randen:", len(randen))
    groepen = vind_verbonen_knopen(randen)
    print("Groepen:", len(groepen))

    id = 0
    unieke_personen = []

    for group in groepen:
        id += 1
        for node in group:
            unieke_personen.append([node, id])

    sla_op_personen(unieke_personen)
    sla_op_groepen(groepen)


maak_unieke_personen()
