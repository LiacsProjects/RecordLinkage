import pandas as pd
import os
import csv


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
        hist = {}

        for size in sizes:
            try:
                hist[size] = hist[size] + 1
            except:
                hist[size] = 1

        print("Group size")
        for i in dict(sorted(hist.items())):
            print(f"{i}, {hist[i]}")


    def find_common_groups(groups1, groups2):
        set1 = set(tuple(sorted(group)) for group in groups1)
        set2 = set(tuple(sorted(group)) for group in groups2)
        common_groups = [list(group) for group in (set1 & set2)]

        return common_groups


    groups1 = load_groups("Unique Individuals\\results\\BL Groups.txt")
    groups2 = load_groups("Unique Individuals\\results\\RL Groups.txt")

    # histogram(groups1, "BL")
    # histogram(groups2, "RL")

    print("Common groups:", len(find_common_groups(groups1, groups2)))


def get_timelines(linker):
    references = get_detailed_references()

    groups = load_groups(f"Unique Individuals\\results\\{linker} Groups.txt")

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
    df_unique_individuals_detailed.to_csv(unique_file_name(f"Unique Individuals\\results\\{linker} Detailed", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


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

    df_pairs = pd.read_csv("RecordLinker\\data\\pairs.csv", sep=";")
    references = {}

    for pair in df_pairs.itertuples():
        if pair.pair == 1:
            references[pair.child_uuid] = {"sex": "?", "name": pair.child, "year": pair.year, "role": 1}
            references[pair.man_uuid] = {"sex": "m", "name": pair.man, "year": pair.year, "role": 2}
            references[pair.woman_uuid] = {"sex": "v", "name": pair.woman, "year": pair.year, "role": 2}
        elif pair.pair == 2:
            references[pair.man_uuid] = {"sex": "m", "name": pair.man, "year": pair.year, "role": 3}
            references[pair.woman_uuid] = {"sex": "v", "name": pair.woman, "year": pair.year, "role": 3}
        elif pair.pair == 3:
            references[pair.child_uuid] = {"sex": "m", "name": pair.child, "year": pair.year, "role": 3}
            references[pair.man_uuid] = {"sex": "m", "name": pair.man, "year": pair.year, "role": 4}
            references[pair.woman_uuid] = {"sex": "v", "name": pair.woman, "year": pair.year, "role": 4}
        elif pair.pair == 4:
            references[pair.child_uuid] = {"sex": "v", "name": pair.child, "year": pair.year, "role": 3}
            references[pair.man_uuid] = {"sex": "m", "name": pair.man, "year": pair.year, "role": 4}
            references[pair.woman_uuid] = {"sex": "v", "name": pair.woman, "year": pair.year, "role": 4}
        elif pair.pair == 5:
            references[pair.man_uuid] = {"sex": "?", "name": pair.man, "year": pair.year, "role": 5}
            references[pair.woman_uuid] = {"sex": "?", "name": pair.woman, "year": pair.year, "role": 6}
        elif pair.pair == 6:
            references[pair.child_uuid] = {"sex": "?", "name": pair.child, "year": pair.year, "role": 5}
            references[pair.man_uuid] = {"sex": "m", "name": pair.man, "year": pair.year, "role": 7}
            references[pair.woman_uuid] = {"sex": "v", "name": pair.woman, "year": pair.year, "role": 7}

    return references
    

def analyse_timelines(linker):
    df_references = pd.read_csv(f"Unique Individuals\\results\\{linker} Detailed.csv", sep=";")

    person = []
    current_id = 1

    histogram_completeness = []
    histogram_born = []
    histogram_child = []
    histogram_died = []
    incorrect = 0

    for reference in df_references.itertuples():
        if reference.unique_person_id != current_id:
            born = 0
            child = 0
            died = 0

            for role in person:
                if role == 1:
                    born += 1
                elif role == 2:
                    child += 1
                elif role == 5:
                    died += 1

            if born == 1 and died == 1:
                histogram_completeness.append("Complete")
            elif born == 1:
                histogram_completeness.append("One birth, no death")
            elif died == 1:
                histogram_completeness.append("One death, no birth")
            else:
                histogram_completeness.append("Other")

            if born > 1 or died > 1:
                incorrect += 1

            histogram_born.append(born)
            histogram_child.append(child)
            histogram_died.append(died)

            current_id += 1
            person = []
            
        person.append(reference.role)

    hists = {"Completeness": histogram_completeness,
            "Born": histogram_born,
            "Died": histogram_died}
    
    for type in hists:
        hist = {}
        for size in hists[type]:
            try:
                hist[size] = hist[size] + 1
            except:
                hist[size] = 1

        print("\n" + type)
        for i in dict(sorted(hist.items())):
            print(f"{i}, {hist[i]}")

    print("\nIncorrect", incorrect)


# get_timelines("RL")
# get_timelines("BL")

# analyse_timelines("RL")
# analyse_timelines("BL")

compare_groups()

