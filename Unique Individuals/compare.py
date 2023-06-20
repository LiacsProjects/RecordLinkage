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
    groups2 = load_groups("Unique Individuals\\results\\BL Groups beter.txt")
    # groups2 = load_groups("Unique Individuals\\results\\RL Groups.txt")

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

    duration = []

    alive_per_year = []

    incorrect_per_year = []
    complete_per_year = []
    only_birth_per_year = []
    only_death_per_year = []
    no_birth_death_per_year = []

    born = []
    married = []
    child = []
    died = []

    birth_not_first = 0
    birth_first = 0

    incorrect = 0
    complete = 0
    only_birth = 0
    only_death = 0
    no_birth_death = 0

    for reference in df_references.itertuples():
        if reference.unique_person_id != current_id:
            documented_years = [year for role, year in person if role not in [4, 6, 7]]
            if len(documented_years) == 0:
                documented_years = [0]

            max_year = max(documented_years)
            min_year = min(documented_years)
            range_life_course = list(range(min_year, max_year + 1))

            alive_per_year += range_life_course
            
            times_born = len([role for role, _ in person if role == 1])
            times_married = len([role for role, _ in person if role == 3])
            times_child = len([role for role, _ in person if role == 2])
            times_died = len([role for role, _ in person if role == 5])

            born.append(times_born)
            married.append(times_married)
            child.append(times_child)
            died.append(times_died)

            if times_born == 1 and times_died == 1:
                complete += 1
                complete_per_year += range_life_course
            elif times_born == 1 and times_died == 0:
                only_birth += 1
                only_birth_per_year += range_life_course
            elif times_born == 0 and times_died == 1:
                only_death += 1
                only_death_per_year += range_life_course
            elif times_born == 0 and times_died == 0:
                no_birth_death += 1
                no_birth_death_per_year += range_life_course
            elif times_born > 1 or times_died > 1:
                incorrect += 1
                incorrect_per_year += range_life_course

            if times_born == 1:
                birth_year = [year for role, year in person if role == 1][0]
                if birth_year == min_year:
                    birth_first += 1
                else:
                    birth_not_first += 1

            duration.append(max_year - min_year)

            current_id += 1
            person = []
            
        person.append((reference.role, reference.year))


    hists = {
        # "born": born,
        # "married": married,
        # "child": child,
        # "died": died,
        # "duration": duration,

        # "alive": alive_per_year,
        # "incorrect": incorrect_per_year,
        # "complete": complete_per_year,
        # "only birth": only_birth_per_year,
        # "only death": only_death_per_year,
        # "no birth/death": no_birth_death_per_year
    }
    
    for hist in hists:
        if hist in ["born", "child", "died", "duration"]:
            print(f"Gemiddeld {hist}", (sum(hists[hist]) / len(hists[hist])))
            values = [value for value in hists[hist] if value > 1]
            print(f"Gemiddeld incorrect {hist}", (sum(values) / len(values)), "\n")

        values = {}
        for value in hists[hist]:
            try:
                values[value] = values[value] + 1
            except:
                values[value] = 1

        print(hist)
        print("year, amount")
        for i in dict(sorted(values.items())):
            print(f"{i}, {values[i]}")
        print("--------------------------\n")

    print("\nComplete:", complete)
    print("Only birth:", only_birth)
    print("Only death:", only_death)
    print("No birth/death:", no_birth_death)
    print("Incorrect:", incorrect)
    print("Som:", complete + only_birth + only_death + no_birth_death + incorrect)


def get_role_hist(linker):
    results = pd.read_csv(f"Unique Individuals\\results\\{linker} Detailed.csv", sep=";")
    hist = {}

    for size in results["role"]:
        try:
            hist[size] = hist[size] + 1
        except:
            hist[size] = 1

    print(linker)
    for i in dict(sorted(hist.items())):
        print(f"{i}, {hist[i]}")


# get_role_hist("BL")
# get_role_hist("RL")

# get_timelines("RL")
# get_timelines("BL")

# analyse_timelines("RL")
analyse_timelines("BL")

# compare_groups()

