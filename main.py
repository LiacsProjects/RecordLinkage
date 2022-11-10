import pandas as pd

print("Reading datasets...")
# df_scheiding_unfiltered = pd.read_csv(r'data\na 1811\Echtscheiding.csv', sep=";")
df_geboorte_unfiltered = pd.read_csv(r'data\na 1811\Geboorte.csv', sep=";", dtype="string")
# df_huwelijk_unfiltered = pd.read_csv(r'data\na 1811\Huwelijk.csv', sep=";")
# df_overlijden_unfiltered = pd.read_csv(r'data\na 1811\Overlijden.csv', sep=";")

print("Filtering datasets...")
# df_scheiding = df_scheiding_unfiltered[["uuid", "Plaats echtscheiding", "Datum echtscheiding", "Datum huwelijk", "Gewezen echtgenoot-Voornaam", "Gewezen echtgenoot-Tussenvoegsel", "Gewezen echtgenoot-Geslachtsnaam", "Gewezen echtgenoot-Beroep", "Gewezen echtgenoot-Plaats wonen", "Gewezen echtgenote-Voornaam", "Gewezen echtgenote-Tussenvoegsel", "Gewezen echtgenote-Geslachtsnaam", "Gewezen echtgenote-Beroep", "Gewezen echtgenote-Plaats wonen"]]
df_geboorte = df_geboorte_unfiltered[["uuid", "Kind-Voornaam", "Kind-Tussenvoegsel", "Kind-Geslachtsnaam", "Kind-Plaats wonen", "Kind-Plaats geboorte", "Kind-Datum geboorte", "Kind-Geslacht", "Vader-Voornaam", "Vader-Tussenvoegsel", "Vader-Geslachtsnaam", "Vader-Plaats wonen", "Vader-Plaats geboorte", "Vader-Datum geboorte", "Vader-Geslacht", "Vader-Beroep", "Vader-Leeftijd", "Moeder-Voornaam", "Moeder-Tussenvoegsel", "Moeder-Geslachtsnaam", "Moeder-Plaats wonen", "Moeder-Plaats geboorte", "Moeder-Datum geboorte", "Moeder-Geslacht", "Moeder-Beroep", "Moeder-Leeftijd", "Getuige-Voornaam", "Getuige-Patroniem", "Getuige-Tussenvoegsel", "Getuige-Geslachtsnaam", "Getuige-Plaats geboorte", "Getuige-Plaats wonen", "Getuige-Datum geboorte", "Getuige-Geslacht", "Getuige-Beroep", "Getuige-Leeftijd"]]
# df_huwelijk = df_huwelijk_unfiltered[[]]


print(df_geboorte.loc[(df_geboorte['Kind-Voornaam'] == "Gerrit Jan") & (df_geboorte['Kind-Geslachtsnaam'] == "Beek")].iloc[0])

# print(df_geboorte)
