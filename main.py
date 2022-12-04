import pandas as pd
from time import time
import Levenshtein
import csv


def generate_processed_data():
    print("Reading datasets...")
    start = time()
    df_geboorte_unfiltered = pd.read_csv(r'data\unprocessed\Geboorte.csv', sep=";", dtype="string") #TODO specify dtype for specific columns
    df_huwelijk_unfiltered = pd.read_csv(r'data\unprocessed\Huwelijk.csv', sep=";", dtype="string")
    df_scheiding_unfiltered = pd.read_csv(r'data\unprocessed\Echtscheiding.csv', sep=";") 
    df_overlijden_unfiltered = pd.read_csv(r'data\unprocessed\Overlijden.csv', sep=";", dtype="string")
    print(f"Completed in {round(time() - start, 2)}s\n")

    print("Filtering datasets...")
    start = time()
    df_geboorte = df_geboorte_unfiltered[["uuid", "Kind-Voornaam", "Kind-Tussenvoegsel", "Kind-Geslachtsnaam", 
        "Kind-Plaats wonen", "Kind-Plaats geboorte", "Kind-Datum geboorte", "Kind-Geslacht", "Vader-Voornaam", 
        "Vader-Tussenvoegsel", "Vader-Geslachtsnaam", "Vader-Plaats wonen", "Vader-Plaats geboorte", "Vader-Datum geboorte", 
        "Vader-Geslacht", "Vader-Beroep", "Vader-Leeftijd", "Moeder-Voornaam", "Moeder-Tussenvoegsel", "Moeder-Geslachtsnaam", 
        "Moeder-Plaats wonen", "Moeder-Plaats geboorte", "Moeder-Datum geboorte", "Moeder-Geslacht", "Moeder-Beroep", 
        "Moeder-Leeftijd", "Getuige-Voornaam", "Getuige-Patroniem", "Getuige-Tussenvoegsel", "Getuige-Geslachtsnaam", 
        "Getuige-Plaats geboorte", "Getuige-Plaats wonen", "Getuige-Datum geboorte", "Getuige-Geslacht", "Getuige-Beroep", 
        "Getuige-Leeftijd"]]

    df_huwelijk = df_huwelijk_unfiltered[["uuid", "Plaats huwelijk", "Datum", "Jaar", "Bruidegom-Voornaam", 
        "Bruidegom-Tussenvoegsel", "Bruidegom-Geslachtsnaam", "Bruidegom-Leeftijd", "Bruidegom-Beroep", 
        "Bruidegom-Plaats geboorte", "Bruidegom-Datum geboorte", "Bruidegom-Plaats wonen", "Vader bruidegom-Voornaam", 
        "Vader bruidegom-Tussenvoegsel", "Vader bruidegom-Geslachtsnaam", "Vader bruidegom-Leeftijd", "Vader bruidegom-Beroep", 
        "Vader bruidegom-Plaats geboorte", "Vader bruidegom-Datum geboorte", "Vader bruidegom-Plaats wonen", 
        "Moeder bruidegom-Voornaam", "Moeder bruidegom-Tussenvoegsel", "Moeder bruidegom-Geslachtsnaam", 
        "Moeder bruidegom-Leeftijd", "Moeder bruidegom-Beroep", "Moeder bruidegom-Plaats geboorte", 
        "Moeder bruidegom-Datum geboorte", "Moeder bruidegom-Plaats wonen", "Bruid-Voornaam", "Bruid-Tussenvoegsel", 
        "Bruid-Geslachtsnaam", "Bruid-Leeftijd", "Bruid-Beroep", "Bruid-Plaats geboorte", "Bruid-Datum geboorte", 
        "Bruid-Plaats wonen", "Vader bruid-Voornaam", "Vader bruid-Tussenvoegsel", "Vader bruid-Geslachtsnaam", 
        "Vader bruid-Leeftijd", "Vader bruid-Beroep", "Vader bruid-Plaats geboorte", "Vader bruid-Datum geboorte", 
        "Vader bruid-Plaats wonen", "Moeder bruid-Voornaam", "Moeder bruid-Tussenvoegsel", "Moeder bruid-Geslachtsnaam", 
        "Moeder bruid-Leeftijd", "Moeder bruid-Beroep", "Moeder bruid-Plaats geboorte", "Moeder bruid-Datum geboorte", 
        "Moeder bruid-Plaats wonen", "Getuige-Voornaam", "Getuige-Patroniem", "Getuige-Tussenvoegsel", "Getuige-Geslachtsnaam", 
        "Getuige-Plaats geboorte", "Getuige-Plaats wonen", "Getuige-Datum geboorte", "Getuige-Geslacht", "Getuige-Beroep", 
        "Getuige-Leeftijd"]]

    df_scheiding = df_scheiding_unfiltered[["uuid", "Plaats echtscheiding", "Datum echtscheiding", "Datum huwelijk", 
        "Gewezen echtgenoot-Voornaam", "Gewezen echtgenoot-Tussenvoegsel", "Gewezen echtgenoot-Geslachtsnaam", 
        "Gewezen echtgenoot-Beroep", "Gewezen echtgenoot-Plaats wonen", "Gewezen echtgenote-Voornaam", 
        "Gewezen echtgenote-Tussenvoegsel", "Gewezen echtgenote-Geslachtsnaam", "Gewezen echtgenote-Beroep", 
        "Gewezen echtgenote-Plaats wonen"]]

    df_overlijden = df_overlijden_unfiltered[["uuid", "Overledene-Voornaam", "Overledene-Tussenvoegsel", 
        "Overledene-Geslachtsnaam", "Overledene-Leeftijd", "Overledene-Beroep", "Overledene-Datum overlijden", 
        "Overledene-Plaats overlijden", "Overledene-Plaats geboorte", "Overledene-Plaats wonen", "Relatie-Voornaam", 
        "Relatie-Tussenvoegsel", "Relatie-Geslachtsnaam", "Relatie-Relatietype", "Relatie-Leeftijd", "Relatie-Beroep", 
        "Relatie-Datum overlijden", "Relatie-Plaats overlijden", "Relatie-Plaats geboorte", "Relatie-Plaats wonen", 
        "Vader-Voornaam", "Vader-Tussenvoegsel", "Vader-Geslachtsnaam", "Vader-Leeftijd", "Vader-Beroep", 
        "Vader-Datum overlijden", "Vader-Plaats overlijden", "Vader-Plaats geboorte", "Vader-Plaats wonen", 
        "Moeder-Voornaam", "Moeder-Tussenvoegsel", "Moeder-Geslachtsnaam", "Moeder-Leeftijd", "Moeder-Beroep", 
        "Moeder-Datum overlijden", "Moeder-Plaats overlijden", "Moeder-Plaats geboorte", "Moeder-Plaats wonen"]]

    print(f"Completed in {round(time() - start, 2)}s\n")

    df_geboorte.to_csv('data\\geboorte.csv')
    df_huwelijk.to_csv('data\\huwelijk.csv')
    df_scheiding.to_csv('data\\scheiding.csv')
    df_overlijden.to_csv('data\\overlijden.csv')

    # print(df_geboorte)
    # print(df_huwelijk)
    # print(df_scheiding)
    # print(df_overlijden)


# generate_processed_data()



# def same_person(person1, person2):
#     results = []
#     role1 = person1[0][9]
#     role2 = person2[0][9]
    

#     for relation in person1:
#         matched = [relation2 for relation2 in person2 if relation2[9] == relation[9]]
#         # print(matched) 
#         if len(matched) == 0:
#             continue
#         elif len(matched) == 1:
#             relation_equivalent = matched[0]
#         else:
#             # TODO Wat nu?
#             relation_equivalent = matched[0]

#         string1 = " ".join(relation[1:6] + [relation[7]] + [relation[8]])
#         string2 = " ".join(relation_equivalent[1:6] + [relation_equivalent[7]] + [relation_equivalent[8]])

#         distance = Levenshtein.distance(string1, string2)
#         results.append([relation[9], distance])
        
#     print(results)    
#     if sum([result[1] for result in results]) / len(results) < 5:
#         return True
#     else:
#         return False      


person1 = [
    [1, "Jan", "van", "Sloot", "Leiden", "02-11-1912", 25, "bakker", "Warmond", ["bruidegom"]],
    [2, "Maria", "", "Janssen", "Leiden", "04-06-1914", 23, "", "Warmond", ["bruid"]],
    [3, "Pien", "", "Janssen", "Warmond", "06-11-1884", 53, "", "Warmond", ["bruid", "moeder"]]
]

person2 = [
    [4, "Jan", "van", "Sloot", "Leiden", "02-10-1912", 25, "bakker", "Warmond", ["bruidegom"]],
    [5, "Marian", "", "Jansen", "Leiden", "04-06-1915", 24, "", "Warmond", ["bruid"]],
    [6, "Pien", "", "Janssen", "Leiden", "06-11-1884", 53, "", "Warmond", ["bruid", "moeder"]],
    [7, "Henk", "", "Janssen", "Hillegom", "25-08-1881", 56, "smidt", "Leiden", ["bruid", "vader"]]
]

person3 = [
    [8, "Jan", "van", "Sloot", "Leiden", "02-10-1912", 54, "bakker", "Warmond", ["bruidegom", "vader"]],
    [9, "Marian", "", "Jansen", "Leiden", "04-06-1915", 52, "", "Warmond", ["bruidegom", "moeder"]],
    [10, "Pien", "", "Janssen", "Leiden", "06-03-1946", 21, "", "Leiden", ["bruid"]],
    [11, "Henk", "", "Janssen", "Hillegom", "14-07-1945", 22, "smidt", "Leiden", ["bruidegom"]]
]
# print(same_person(person1, person2))





# def get_levenshtein_distance(string1, string2):
#     return Levenshtein.distance(string1, string2)

# print(get_levenshtein_distance("test1", "test2"))


def same_person(person1, person2):

    cols = [2,3,4,6,7,8,9]
    attrs1 = []
    attrs2 = []

    for col in cols:
        if person1[col] != '' and person2[col] != '':
            attrs1.append(person1[col])
            attrs2.append(person2[col])

    distance = Levenshtein.distance(" ".join(attrs1), " ".join(attrs2))

    if distance < len(attrs1):
        return True
    else:
        return False


def generate_persons():
    # df_geboorte = pd.read_csv(r'data\geboorte.csv', sep=";", dtype="string")
    df_huwelijk = pd.read_csv(r'data\huwelijk.csv', dtype="string")
    # df_scheiding = pd.read_csv(r'data\echtscheiding.csv', sep=";") 
    # df_overlijden = pd.read_csv(r'data\overlijden.csv', sep=";", dtype="string")

    # df_persons = pd.DataFrame(data={'pid': [], 'Voornaam': [], 'Tussenvoegsel': [], 'Achternaam': [], 'Voornaam': []})
    # print(df_persons)
    # row = next(df_huwelijk.iterrows())[1]

    # print(row["uuid"])
    count = 0
    all_persons = []
    for huwelijk in df_huwelijk.iterrows():
        # print(huwelijk[1])

        persons = []

        persons.append([count, str(huwelijk[1]["uuid"]).strip(), 
        str(huwelijk[1]["Bruidegom-Voornaam"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Bruidegom-Tussenvoegsel"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Bruidegom-Geslachtsnaam"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Bruidegom-Leeftijd"]).replace("<NA>", "").lower().replace("jaar", "").strip(), 
        str(huwelijk[1]["Bruidegom-Beroep"]).replace("<NA>", "").lower().replace("beroep", "").strip(), 
        str(huwelijk[1]["Bruidegom-Plaats geboorte"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Bruidegom-Datum geboorte"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Bruidegom-Plaats wonen"]).replace("<NA>", "").lower().strip(), ["bruidegom"]])
        count += 1

        persons.append([count, str(huwelijk[1]["uuid"]).strip(), 
        str(huwelijk[1]["Vader bruidegom-Voornaam"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Vader bruidegom-Tussenvoegsel"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Vader bruidegom-Geslachtsnaam"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Vader bruidegom-Leeftijd"]).replace("<NA>", "").lower().replace("jaar", "").strip(), 
        str(huwelijk[1]["Vader bruidegom-Beroep"]).replace("<NA>", "").lower().replace("beroep", "").strip(), 
        str(huwelijk[1]["Vader bruidegom-Plaats geboorte"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Vader bruidegom-Datum geboorte"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Vader bruidegom-Plaats wonen"]).replace("<NA>", "").lower().strip(), ["bruidegom", "vader"]])
        count += 1

        persons.append([count, str(huwelijk[1]["uuid"]).strip(), 
        str(huwelijk[1]["Vader bruid-Voornaam"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Vader bruid-Tussenvoegsel"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Vader bruid-Geslachtsnaam"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Vader bruid-Leeftijd"]).replace("<NA>", "").lower().replace("jaar", "").strip(), 
        str(huwelijk[1]["Vader bruid-Beroep"]).replace("<NA>", "").lower().replace("beroep", "").strip(), 
        str(huwelijk[1]["Vader bruid-Plaats geboorte"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Vader bruid-Datum geboorte"]).replace("<NA>", "").lower().strip(), 
        str(huwelijk[1]["Vader bruid-Plaats wonen"]).replace("<NA>", "").lower().strip(), ["bruidegom", "vader"]])
        count += 1

        all_persons.append(persons) 

        # print(persons)

    # print(all_persons)
    return all_persons


persons = generate_persons()

matches = []

for certificate in persons:
    print(certificate)
    for person1 in certificate:
        for certificate2 in persons:
            for person2 in certificate2:
                if same_person(person1, person2):
                    matches.append([person1[0], person2[0], person1[1], person2[1]])
                    print(person1, person2)
    break

with open("matches.csv", "w", newline='') as f:
    write = csv.writer(f)
    write.writerow(["p1 id", "p2 id", "cert 1", "cert 2"])
    for match in matches:
        write.writerow(match)

