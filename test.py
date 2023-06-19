import pandas as pd
import matplotlib.pyplot as plt

meer = pd.read_csv("Unique Individuals\\results\\BL Detailed (1).csv", sep=";")
# minder = pd.read_csv("Unique Individuals\\results\\BL Detailed slechter.csv", sep=";")
minder = pd.read_csv("Unique Individuals\\results\\RL Detailed.csv", sep=";")

hist = {}
for size in meer["role"]:
    try:
        hist[size] = hist[size] + 1
    except:
        hist[size] = 1

print("Huidig")
for i in dict(sorted(hist.items())):
    print(f"{i}, {hist[i]}")

hist = {}
for size in minder["role"]:
    try:
        hist[size] = hist[size] + 1
    except:
        hist[size] = 1

print("vroeger")
for i in dict(sorted(hist.items())):
    print(f"{i}, {hist[i]}")




