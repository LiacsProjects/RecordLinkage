import pandas as pd
import csv


def set_comparison():

    df_links_rl = pd.read_csv("results\\Links Persons RecordLinker.csv", sep=";")
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

    
set_comparison()

