import pandas as pd
import csv

INDEX_GROOM = 30
INDEX_GROOM_FATHER = 48
INDEX_GROOM_MOTHER = 66
INDEX_BRIDE = 84
INDEX_BRIDE_FATHER = 102
INDEX_BRIDE_MOTHER = 120


def get_match_uuid():
    df_matches = pd.read_csv("matches.csv", sep=";")
    id_map = pd.read_csv("registrations.csv", sep=";")

    matches = []
    for row in df_matches.itertuples():
        id_certificate_parents = id_map.loc[id_map['id_registration'] == row.id_certificate_parents].iloc[0]['registration_seq']
        id_certificate_partners = id_map.loc[id_map['id_registration'] == row.id_certificate_partners].iloc[0]['registration_seq']

        matches.append([id_certificate_parents, id_certificate_partners])
    
    df_clean_matches = pd.DataFrame(matches, columns=["parents_id", "partners_id"])
    df_clean_matches.to_csv("clean matches.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)



def clean(value):
    return str(value).replace("<NA>", "").strip()


def generate_persons():

    def get_date(date:str):

        def keep_numeric(text):
            return int("".join([ch for ch in text if ch.isnumeric()]))

        try:
            date_list = date.split("-")
            if date[2] == "-":
                index_day, index_month, index_year = 0, 1, 2
            else:
                index_day, index_month, index_year = 2, 1, 0

            return keep_numeric(date_list[index_day]), keep_numeric(date_list[index_month]), keep_numeric(date_list[index_year])

        except Exception as e:
            # print(e, "date")
            return 0, 0, 0


    def get_age(age_raw:str):
        try:
            age = ''
            for ch in age_raw:
                if ch.isnumeric():  
                    age += ch

            if len(age) > 0:
                return int(age)
            else:
                return 0
        except Exception as e:
            # print(e, "age")
            return 0


    def get_index(role):
        if role == "Bruidegom":
            return INDEX_GROOM
        if role == "Vader bruidegom":
            return INDEX_GROOM_FATHER
        if role == "Moeder bruidegom":
            return INDEX_GROOM_MOTHER
        if role == "Bruid":
            return INDEX_BRIDE
        if role == "Vader bruid":
            return INDEX_BRIDE_FATHER
        if role == "Moeder bruid":
            return INDEX_BRIDE_MOTHER
    

    df_marriage_unfiltered = pd.read_csv(r'data\unprocessed\Huwelijk.csv', sep=";", dtype="string")
    persons = []
    marriages = []
    person_id = 0

    for marriage_unfiltered in df_marriage_unfiltered.itertuples():
        day, month, year = get_date(marriage_unfiltered[27])

        marriage = [
            marriage_unfiltered[0],                     # id
            marriage_unfiltered[1],                     # uuid
            day, month, year]                           # Date

        marriages.append(marriage)
    
        for role in ["Bruidegom", "Vader bruidegom", "Moeder bruidegom", "Bruid", "Vader bruid", "Moeder bruid"]:
            index = get_index(role)
            birth_day, birth_month, birth_year = get_date(clean(marriage_unfiltered[index + 15]))

            person = [
                person_id,                                          # id
                marriage_unfiltered[index],                         # uuid
                role,                                               # Role
                clean(marriage_unfiltered[index + 9]),              # Voornaam
                clean(marriage_unfiltered[index + 10]),             # Tussenvoegsel
                clean(marriage_unfiltered[index + 11]),             # Geslachtsnaam
                get_age(clean(marriage_unfiltered[index + 12])),    # Age
                clean(marriage_unfiltered[index + 13]),             # Beroep
                clean(marriage_unfiltered[index + 14]),             # Geboorte plaats
                birth_day, birth_month, birth_year,                 # Geboorte datum
                clean(marriage_unfiltered[index + 16])]             # Woonplaats
            
            persons.append(person)
            person_id += 1


    df_marriage = pd.DataFrame(marriages, columns=[
        "id", 
        "uuid", 
        "dag", 
        "maand", 
        "jaar"])

    df_persons = pd.DataFrame(persons, columns=[
        "id", 
        "uuid", 
        "rol", 
        "voornaam", 
        "tussenvoegsel", 
        "geslachtsnaam", 
        "leeftijd", 
        "beroep", 
        "geboorteplaats", 
        "dag",
        "maand", 
        "jaar", 
        "woonplaats"])

    df_marriage.to_csv("marriages.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
    df_persons.to_csv("persons.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


def get_relations():
    def valid_name(self, person_id):
        first_name = self.df_persons.at[person_id, "voornaam"]
        if isinstance(first_name, str):
            return True
        return False
    
    df_marriages = pd.read_csv("marriages met uuid.csv", sep=";")
    df_persons = pd.read_csv("persons.csv", sep=";")

    relations = []
    for marriage in df_marriages.itertuples():
        print(marriage)
        for index, i in enumerate(marriage[6:]):
            print(index, i)
        if valid_name():
            relations.append(marriage.bruidegom_uuid, marriage.vader_bruidegom_uuid, "zoon")
            
            relations.append(marriage.bruidegom_uuid, marriage.moeder_bruidegom_uuid, "zoon")
            relations.append(marriage.bruid_uuid, marriage.vader_bruid_uuid, "dochter")
            relations.append(marriage.bruid_uuid, marriage.moeder_bruid_uuid, "dochter")


        break
        # if valid_name():
        #     relation = 


        # relations.append(relations)

get_relations()