import pandas as pd
import os
import matplotlib.pyplot as plt
import csv


def set_comparison():

    df_links_rl = pd.read_csv("results\\Links Persons RecordLinker (2).csv", sep=";")
    df_links_rl = df_links_rl[df_links_rl["mode"] != 4]
    df_links_rl = df_links_rl[df_links_rl["mode"] != 3]

    df_links_bl = pd.read_csv("data\\results\\links h persons.csv", sep=";")
    df_links_bl = pd.concat([df_links_bl, pd.read_csv("data\\results\\links b persons.csv", sep=";")])

    links_rl = set()
    links_bl = set()

    print("rl", len(df_links_rl.index))
    print("bl", len(df_links_bl.index))

    for i in df_links_rl.itertuples():
        links_rl.add(i.reference_uuid + i.link_uuid)

    for j in df_links_bl.itertuples():
        links_bl.add(j.reference_uuid + j.link_uuid)

    n = len(links_rl | links_bl)
    print("rl | bl", n)

    x = len(links_rl - links_bl)
    print("rl - bl", x)

    y = len(links_bl - links_rl)
    print("bl - rl", y)

    z = len(links_bl & links_rl)
    print("bl & rl", z)


def unique_file_name(path, extension = ""):
    i = 0
    temp_path = path
    while os.path.exists(temp_path + "." + extension):  #check of het bestand al bestaat
        i += 1
        temp_path = path + " ({})".format(str(i))
    return temp_path + "." + extension


def load_groups(filename):
    with open(filename, 'r') as f:
        groups = [[str(node) for node in line.strip().split(',')] for line in f.readlines()]
    return groups
    

def compare_groups():
    def histogram(groups, method):
        sizes = [len(group) for group in groups]
        print(method)
        print("Aantal:", len(sizes))
        print("Average:", sum(sizes) / len(sizes), "\n")

        # Plot histogram
        plt.hist(sizes, bins=range(1, max(sizes) + 2), align="left")

        # Set axis labels and title
        plt.xlabel("References per Unique Historical Individual")
        plt.ylabel("Frequency")
        plt.yscale("log")
        plt.title(f"Histogram of References per Unique Historical Individual ({method})")

        # Save plot
        # plt.show()
        plt.savefig(unique_file_name("results\\unique\\" + method + " Histogram", "svg"))


    def find_common_groups(groups1, groups2):
        set1 = set(tuple(sorted(group)) for group in groups1)
        set2 = set(tuple(sorted(group)) for group in groups2)
        common_groups = [list(group) for group in (set1 & set2)]

        return common_groups


    groups1 = load_groups("results\\unique\\BL Groups.txt")
    groups2 = load_groups("results\\unique\\RL Groups.txt")

    histogram(groups1, "BL")
    histogram(groups2, "RL")

    print("Common groups:", len(find_common_groups(groups1, groups2)))


def get_timelines(linker):
    references = get_detailed_references()

    groups = load_groups(f"results\\unique\\{linker} Groups.txt")

    unique_individuals_detailed = []
    unique_identifier = 1

    errors = 0

    for group in groups:

        for uuid in group:
            try:
                person = references[uuid]
                unique_individuals_detailed.append([uuid, person["role"], person["name"], person["year"], unique_identifier])
            except:
                errors += 1
        
        unique_identifier += 1

    print("Errors:", errors)
    print("Amount of persons:", unique_identifier)

    df_unique_individuals_detailed = pd.DataFrame(unique_individuals_detailed, columns=["uuid", "role", "name", "year", "unique_person_id"])
    df_unique_individuals_detailed.to_csv(unique_file_name(f"results\\unique\\{linker} Detailed", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


def get_detailed_references():
    """
    1: Born
    2: Child born
    3: Married
    4: Child married
    5: Died
    6: Partner died
    7: Child died
    """

    df_pairs = pd.read_csv("data\\pairs.csv", sep=";")
    references = {}

    for pair in df_pairs.itertuples():
        if pair.role == 4:
            references[pair.child_uuid] = {"sex": "?", "name": pair.child, "year": pair.year, "role": 1}
            references[pair.man_uuid] = {"sex": "m", "name": pair.man, "year": pair.year, "role": 2}
            references[pair.woman_uuid] = {"sex": "v", "name": pair.woman, "year": pair.year, "role": 2}
        elif pair.role == 1:
            references[pair.man_uuid] = {"sex": "m", "name": pair.man, "year": pair.year, "role": 3}
            references[pair.woman_uuid] = {"sex": "v", "name": pair.woman, "year": pair.year, "role": 3}
        elif pair.role == 2:
            references[pair.child_uuid] = {"sex": "m", "name": pair.child, "year": pair.year, "role": 3}
            references[pair.man_uuid] = {"sex": "m", "name": pair.man, "year": pair.year, "role": 4}
            references[pair.woman_uuid] = {"sex": "v", "name": pair.woman, "year": pair.year, "role": 4}
        elif pair.role == 3:
            references[pair.child_uuid] = {"sex": "v", "name": pair.child, "year": pair.year, "role": 3}
            references[pair.man_uuid] = {"sex": "m", "name": pair.man, "year": pair.year, "role": 4}
            references[pair.woman_uuid] = {"sex": "v", "name": pair.woman, "year": pair.year, "role": 4}
        elif pair.role == 5:
            references[pair.man_uuid] = {"sex": "?", "name": pair.man, "year": pair.year, "role": 5}
            references[pair.woman_uuid] = {"sex": "?", "name": pair.woman, "year": pair.year, "role": 6}
        elif pair.role == 6:
            references[pair.child_uuid] = {"sex": "?", "name": pair.child, "year": pair.year, "role": 5}
            references[pair.man_uuid] = {"sex": "m", "name": pair.man, "year": pair.year, "role": 7}
            references[pair.woman_uuid] = {"sex": "v", "name": pair.woman, "year": pair.year, "role": 7}

    return references
    

def analyse_timelines(linker):
    df_references = pd.read_csv(f"results\\unique\\{linker} Detailed.csv", sep=";")

    # person = pd.DataFrame(columns=["role", "name", "year"])
    person = []
    current_id = 1

    histogram_completeness = []
    histogram_born = []
    histogram_child = []
    histogram_died = []

    for reference in df_references.itertuples():
        if reference.unique_person_id != current_id:
            born = 0
            child = 0
            died = 0

            for role in person:
                if role == 1:
                    born += 1
                elif role in [2, 4, 7]:
                    child += 1
                elif role == 5:
                    died += 1

            if born == 1 and child > 0 and died == 1:
                histogram_completeness.append("4")
            elif born == 1 and died == 1:
                histogram_completeness.append("3")
            elif born == 1:
                histogram_completeness.append("2")
            elif died == 1:
                histogram_completeness.append("1")
            else:
                histogram_completeness.append("0")

            histogram_born.append(str(born))
            histogram_child.append(str(child))
            histogram_died.append(str(died))

            # TODO valideer volgorde
            # person = pd.DataFrame(columns=["role", "name", "year"])
            person = []
            
        person.append(reference.role)

    data = {"completeness": histogram_completeness,
            "born": histogram_born,
            "child": histogram_child,
            "died": histogram_died}
    
    df_histograms = pd.DataFrame(data)
    df_histograms.to_csv(f"results\\unique\\Analyse\\{linker} Histograms.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
    # with open(f"results\\unique\\Analyse\\{linker} hist complete", "w") as f:
    #     f.write("\n".join(histogram_completeness))
    # with open(f"results\\unique\\Analyse\\{linker} hist born", "w") as f:
    #     f.write("\n".join(histogram_born))
    # with open(f"results\\unique\\Analyse\\{linker} hist child", "w") as f:
    #     f.write("\n".join(histogram_child))
    # with open(f"results\\unique\\Analyse\\{linker} hist died", "w") as f:
    #     f.write("\n".join(histogram_died))


# get_timelines("RL")
# get_timelines("BL")

# analyse_timelines("RL")
analyse_timelines("BL")


