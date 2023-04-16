import pandas as pd
import os
import matplotlib.pyplot as plt

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

    
def compare_groups():
    def histogram(groups, filename):
        sizes = [len(group) for group in groups]

        # Plot histogram
        plt.hist(sizes, bins=range(1, max(sizes) + 2), align='left')

        # Set axis labels and title
        plt.xlabel('Group size')
        plt.ylabel('Frequency')
        plt.title('Histogram of group sizes')

        # Save plot
        # plt.show()
        plt.savefig(unique_file_name("results\\unique\\" + filename, "svg"))


    def load_groups(filename):
        with open(filename, 'r') as f:
            groups = [[str(node) for node in line.strip().split(',')] for line in f.readlines()]
        return groups


    def find_common_groups(groups1, groups2):
        set1 = set(tuple(sorted(group)) for group in groups1)
        set2 = set(tuple(sorted(group)) for group in groups2)
        common_groups = [list(group) for group in (set1 & set2)]

        return common_groups


    groups1 = load_groups("results\\unique\\BL Groups.txt")
    groups2 = load_groups("results\\unique\\RL Groups.txt")

    histogram(groups1, "BL Histogram")
    histogram(groups2, "RL Histogram")

    print("Common groups:",len(find_common_groups(groups1, groups2)))


compare_groups()

