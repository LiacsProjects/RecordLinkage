import pandas as pd
from time import time

print("Reading datasets...")
start = time()
df_geboorte_unfiltered = pd.read_csv(r'data\na 1811\Geboorte.csv', sep=";", dtype="string") #TODO specify dtype for specific columns
df_huwelijk_unfiltered = pd.read_csv(r'data\na 1811\Huwelijk.csv', sep=";", dtype="string")
df_scheiding_unfiltered = pd.read_csv(r'data\na 1811\Echtscheiding.csv', sep=";") 
df_overlijden_unfiltered = pd.read_csv(r'data\na 1811\Overlijden.csv', sep=";", dtype="string")
print(f"Completed in {round(time() - start, 2)}s\n")

print("Filtering datasets...")
start = time()
df_geboorte = df_geboorte_unfiltered[["uuid", "Kind-Voornaam", "Kind-Tussenvoegsel", "Kind-Geslachtsnaam", "Kind-Plaats wonen", "Kind-Plaats geboorte", "Kind-Datum geboorte", "Kind-Geslacht", "Vader-Voornaam", "Vader-Tussenvoegsel", "Vader-Geslachtsnaam", "Vader-Plaats wonen", "Vader-Plaats geboorte", "Vader-Datum geboorte", "Vader-Geslacht", "Vader-Beroep", "Vader-Leeftijd", "Moeder-Voornaam", "Moeder-Tussenvoegsel", "Moeder-Geslachtsnaam", "Moeder-Plaats wonen", "Moeder-Plaats geboorte", "Moeder-Datum geboorte", "Moeder-Geslacht", "Moeder-Beroep", "Moeder-Leeftijd", "Getuige-Voornaam", "Getuige-Patroniem", "Getuige-Tussenvoegsel", "Getuige-Geslachtsnaam", "Getuige-Plaats geboorte", "Getuige-Plaats wonen", "Getuige-Datum geboorte", "Getuige-Geslacht", "Getuige-Beroep", "Getuige-Leeftijd"]]
df_huwelijk = df_huwelijk_unfiltered[["uuid", "Plaats huwelijk", "Datum", "Jaar", "Bruidegom-Voornaam", "Bruidegom-Tussenvoegsel", "Bruidegom-Geslachtsnaam", "Bruidegom-Leeftijd", "Bruidegom-Beroep", "Bruidegom-Plaats geboorte", "Bruidegom-Datum geboorte", "Bruidegom-Plaats wonen", "Vader bruidegom-Voornaam", "Vader bruidegom-Tussenvoegsel", "Vader bruidegom-Geslachtsnaam", "Vader bruidegom-Leeftijd", "Vader bruidegom-Beroep", "Vader bruidegom-Plaats geboorte", "Vader bruidegom-Datum geboorte", "Vader bruidegom-Plaats wonen", "Moeder bruidegom-Voornaam", "Moeder bruidegom-Tussenvoegsel", "Moeder bruidegom-Geslachtsnaam", "Moeder bruidegom-Leeftijd", "Moeder bruidegom-Beroep", "Moeder bruidegom-Plaats geboorte", "Moeder bruidegom-Datum geboorte", "Moeder bruidegom-Plaats wonen", "Bruid-Voornaam", "Bruid-Tussenvoegsel", "Bruid-Geslachtsnaam", "Bruid-Leeftijd", "Bruid-Beroep", "Bruid-Plaats geboorte", "Bruid-Datum geboorte", "Bruid-Plaats wonen", "Vader bruid-Voornaam", "Vader bruid-Tussenvoegsel", "Vader bruid-Geslachtsnaam", "Vader bruid-Leeftijd", "Vader bruid-Beroep", "Vader bruid-Plaats geboorte", "Vader bruid-Datum geboorte", "Vader bruid-Plaats wonen", "Moeder bruid-Voornaam", "Moeder bruid-Tussenvoegsel", "Moeder bruid-Geslachtsnaam", "Moeder bruid-Leeftijd", "Moeder bruid-Beroep", "Moeder bruid-Plaats geboorte", "Moeder bruid-Datum geboorte", "Moeder bruid-Plaats wonen", "Getuige-Voornaam", "Getuige-Patroniem", "Getuige-Tussenvoegsel", "Getuige-Geslachtsnaam", "Getuige-Plaats geboorte", "Getuige-Plaats wonen", "Getuige-Datum geboorte", "Getuige-Geslacht", "Getuige-Beroep", "Getuige-Leeftijd"]]
df_scheiding = df_scheiding_unfiltered[["uuid", "Plaats echtscheiding", "Datum echtscheiding", "Datum huwelijk", "Gewezen echtgenoot-Voornaam", "Gewezen echtgenoot-Tussenvoegsel", "Gewezen echtgenoot-Geslachtsnaam", "Gewezen echtgenoot-Beroep", "Gewezen echtgenoot-Plaats wonen", "Gewezen echtgenote-Voornaam", "Gewezen echtgenote-Tussenvoegsel", "Gewezen echtgenote-Geslachtsnaam", "Gewezen echtgenote-Beroep", "Gewezen echtgenote-Plaats wonen"]]
df_overlijden = df_overlijden_unfiltered[["uuid", "Overledene-Voornaam", "Overledene-Tussenvoegsel", "Overledene-Geslachtsnaam", "Overledene-Leeftijd", "Overledene-Beroep", "Overledene-Datum overlijden", "Overledene-Plaats overlijden", "Overledene-Plaats geboorte", "Overledene-Plaats wonen", "Relatie-Voornaam", "Relatie-Tussenvoegsel", "Relatie-Geslachtsnaam", "Relatie-Relatietype", "Relatie-Leeftijd", "Relatie-Beroep", "Relatie-Datum overlijden", "Relatie-Plaats overlijden", "Relatie-Plaats geboorte", "Relatie-Plaats wonen", "Vader-Voornaam", "Vader-Tussenvoegsel", "Vader-Geslachtsnaam", "Vader-Leeftijd", "Vader-Beroep", "Vader-Datum overlijden", "Vader-Plaats overlijden", "Vader-Plaats geboorte", "Vader-Plaats wonen", "Moeder-Voornaam", "Moeder-Tussenvoegsel", "Moeder-Geslachtsnaam", "Moeder-Leeftijd", "Moeder-Beroep", "Moeder-Datum overlijden", "Moeder-Plaats overlijden", "Moeder-Plaats geboorte", "Moeder-Plaats wonen"]]
print(f"Completed in {round(time() - start, 2)}s\n")

# print(df_geboorte)
# print(df_huwelijk)
# print(df_scheiding)
# print(df_overlijden)

