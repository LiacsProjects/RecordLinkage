import pandas as pd
import csv

INDEX_GROOM = 30
INDEX_GROOM_FATHER = 48
INDEX_GROOM_MOTHER = 66
INDEX_BRIDE = 84
INDEX_BRIDE_FATHER = 102
INDEX_BRIDE_MOTHER = 120
INDEX_CHILD = 29
INDEX_FATHER = 48
INDEX_MOTHER = 67


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


def get_link_uuid_birth():
    df_marriages = pd.read_csv("data\\burgerLinker\\Marriages\\registrations.csv", sep=";", )
    df_births = pd.read_csv("data\\burgerLinker\\Births\\registrations.csv", sep=";")
    df_links = pd.read_csv("data\\links b.csv", sep=",")

    links_uuid = []
    for link in df_links.itertuples():     
        marriage_uuid = df_marriages.loc[df_marriages['id_registration'] == link.id_certificate_partners].iloc[0]['registration_seq']
        birth_uuid = df_births.loc[df_births['id_registration'] == link.id_certificate_newbornParents].iloc[0]['registration_seq']

        links_uuid.append([birth_uuid, marriage_uuid])

    df_clean_matches = pd.DataFrame(links_uuid, columns=["birth_id", "marriage_id"])
    df_clean_matches.to_csv("data\\link b uuid.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


def clean(value):
    return str(value).replace("<NA>", "").strip()


def generate_persons_marriage():

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


def generate_persons_birth():

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
        if role == "Kind":
            return INDEX_CHILD
        if role == "Vader":
            return INDEX_FATHER
        if role == "Moeder":
            return INDEX_MOTHER
    

    df_births_unfiltered = pd.read_csv(r'data\unprocessed\Geboorte.csv', sep=";", dtype="string")
    persons = []
    births = []
    person_id = 0

    for birth_unfiltered in df_births_unfiltered.itertuples():
        day, month, year = get_date(birth_unfiltered[43])        

        birth = [
            birth_unfiltered[0],                     # id
            birth_unfiltered[1],                     # uuid
            day, month, year]                           # Date

        # print(birth)
        births.append(birth)
    
        for role in ["Kind", "Vader", "Moeder"]:
            index = get_index(role)
            birth_day, birth_month, birth_year = get_date(clean(birth_unfiltered[index + 14]))

            person = [
                person_id,                                          # id
                birth_unfiltered[index],                         # uuid
                role,                                               # Role
                clean(birth_unfiltered[index + 9]),              # Voornaam
                clean(birth_unfiltered[index + 10]),             # Tussenvoegsel
                clean(birth_unfiltered[index + 11]),             # Geslachtsnaam
                get_age(clean(birth_unfiltered[index + 17])),    # Age
                clean(birth_unfiltered[index + 16]),             # Beroep
                clean(birth_unfiltered[index + 13]),             # Geboorte plaats
                birth_day, birth_month, birth_year,                 # Geboorte datum
                clean(birth_unfiltered[index + 12])]             # Woonplaats
            
            persons.append(person)
            person_id += 1
            # print(person)

        # break


    df_births = pd.DataFrame(births, columns=[
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

    df_births.to_csv("births.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
    df_persons.to_csv("persons.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


def get_relations():  
    df_marriages = pd.read_csv("data\\marriages met uuid.csv", sep=";")
    df_persons = pd.read_csv("data\\persons.csv", sep=";")

    relations = []

    def valid_name(person_id):
        first_name = df_persons.at[person_id, "voornaam"]
        if isinstance(first_name, str):
            return True
        return False


    for marriage in df_marriages.itertuples():
        groom_father_id = marriage.id * 6 + 1
        groom_mother_id = marriage.id * 6 + 2
        bride_father_id = marriage.id * 6 + 4
        bride_mother_id = marriage.id * 6 + 5

        relations.append([marriage.bruidegom_uuid, marriage.bruid_uuid, "m", "v", "partner"])
        if valid_name(groom_father_id):
            relations.append([marriage.bruidegom_uuid, marriage.vader_bruidegom_uuid, "m", "m", "zoon"])
        if valid_name(groom_mother_id):
            relations.append([marriage.bruidegom_uuid, marriage.moeder_bruidegom_uuid, "m", "v", "zoon"])
        if valid_name(bride_father_id):    
            relations.append([marriage.bruid_uuid, marriage.vader_bruid_uuid, "v", "m", "dochter"])
        if valid_name(bride_mother_id):
            relations.append([marriage.bruid_uuid, marriage.moeder_bruid_uuid, "v", "v", "dochter"])
        


    df_relations = pd.DataFrame(relations, columns=["rel1_id", "rel2_id", "rel1_sex", "rel2_sex", "rel_type"])
    df_relations.to_csv("data\\relations.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)    


# generate_persons_birth()

