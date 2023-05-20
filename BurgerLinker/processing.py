import Levenshtein
import pandas as pd
import csv
import os
import re
from os.path import isfile, join

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


def unique_file_name(path, extension = ""):
    i = 0
    temp_path = path
    while os.path.exists(temp_path + "." + extension):  #check of het bestand al bestaat
        i += 1
        temp_path = path + " ({})".format(str(i))
    return temp_path + "." + extension


class GeneratePersonLinks():
    def __init__(self):
            self.df_births = pd.read_csv("data\\burgerLinker\\input\\Births\\persons.csv", sep=";")
            self.df_marriage = pd.read_csv("data\\burgerLinker\\input\\Marriages\\persons.csv", sep=";")
            self.df_deaths = pd.read_csv("data\\burgerLinker\\input\\Deaths\\persons.csv", sep=";")
            self.links = []


    def get_uuid_B_M(self):
        df_links = pd.read_csv("data\\burgerLinker\\output\\raw\\within-B-M-maxLev-3.csv", sep=",")

        for link in df_links.itertuples():
            persons = self.df_births[self.df_births["id_registration"] == link.id_certificate_newborn]
            child = persons[persons["role"] == 1]

            persons = self.df_marriage[self.df_marriage["id_registration"] == link.id_certificate_partner]
            groom = persons[persons["role"] == 7]
            bride = persons[persons["role"] == 4]

            child_name = child.iloc[0]["firstname"] + child.iloc[0]["familyname"]
            is_groom = True
            try:
                groom_name = groom.iloc[0]["firstname"] + groom.iloc[0]["familyname"]
                try:
                    bride_name = bride.iloc[0]["firstname"] + bride.iloc[0]["familyname"]
                    
                    if Levenshtein.distance(child_name, groom_name) > Levenshtein.distance(child_name, bride_name):
                        is_groom = False
                except:
                    pass
            except:
                is_groom = False

            if is_groom == "groom":
                self.links.append([1, child.iloc[0]["uuid"], groom.iloc[0]["uuid"], "m"])
            else:
                self.links.append([1, child.iloc[0]["uuid"], bride.iloc[0]["uuid"], "v"])

            break


        df_links = pd.read_csv("data\\burgerLinker\\output\\raw\\between-B-M-maxLev-3.csv", sep=",")

        for link in df_links.itertuples():
            persons = self.df_births[self.df_births["id_registration"] == link.id_certificate_newbornParents]
            father = persons[persons["role"] == 3].iloc[0]["uuid"]
            mother = persons[persons["role"] == 2].iloc[0]["uuid"]

            persons = self.df_marriage[self.df_marriage["id_registration"] == link.id_certificate_partners]
            groom = persons[persons["role"] == 7].iloc[0]["uuid"]
            bride = persons[persons["role"] == 4].iloc[0]["uuid"]

            self.links.append([2, father, groom, "m"])
            self.links.append([2, mother, bride, "v"])


            break


    def get_uuid_D_M(self):
        df_links = pd.read_csv("data\\burgerLinker\\output\\raw\\between-D-M-maxLev-3.csv", sep=",")

        for link in df_links.itertuples():
            persons = self.df_marriage[self.df_marriage["id_registration"] == link.id_certificate_partners]
            groom = persons[persons["role"] == 7].iloc[0]["uuid"]
            bride = persons[persons["role"] == 4].iloc[0]["uuid"]

            persons = self.df_deaths[self.df_deaths["id_registration"] == link.id_certificate_deceasedParents]
            father = persons[persons["role"] == 3].iloc[0]["uuid"]
            mother = persons[persons["role"] == 2].iloc[0]["uuid"]

            self.links.append([3, father, groom, "m"])
            self.links.append([3, mother, bride, "v"])

            break


    def get_uuid_M_M(self):
        df_links = pd.read_csv("data\\burgerLinker\\output\\raw\\between-M-M-maxLev-3.csv", sep=",")

        for link in df_links.itertuples():
            persons = self.df_marriage[self.df_marriage["id_registration"] == link.id_certificate_partners]
            groom = persons[persons["role"] == 7].iloc[0]
            bride = persons[persons["role"] == 4].iloc[0]

            persons = self.df_marriage[self.df_marriage["id_registration"] == link.id_certificate_parents]
            groom_father = persons[persons["role"] == 9]
            groom_mother = persons[persons["role"] == 8]

            bride_father = persons[persons["role"] == 6]
            bride_mother = persons[persons["role"] == 5]

            partners_name = groom["firstname"] + groom["familyname"] + bride["firstname"] + bride["familyname"]
            parents_of = "groom"
            try:
                groom_parents_name = groom_father.iloc[0]["firstname"] + groom_father.iloc[0]["familyname"] + groom_mother.iloc[0]["firstname"] + groom_mother.iloc[0]["familyname"]
                try:
                    bride_parents_name = bride_father.iloc[0]["firstname"] + bride_father.iloc[0]["familyname"] + bride_mother.iloc[0]["firstname"] + bride_mother.iloc[0]["familyname"]
                    
                    if Levenshtein.distance(partners_name, groom_parents_name) > Levenshtein.distance(partners_name, bride_parents_name):
                        parents_of = "bride"
                except:
                    pass
            except:
                parents_of = "bride"

            if parents_of == "groom":
                self.links.append([4, groom_father.iloc[0]["uuid"], groom["uuid"], "m"])
                self.links.append([4, groom_mother.iloc[0]["uuid"], bride["uuid"], "v"])
            elif parents_of == "bride":
                self.links.append([4, bride_father.iloc[0]["uuid"], groom["uuid"], "m"])
                self.links.append([4, bride_mother.iloc[0]["uuid"], bride["uuid"], "v"])

            break


    def get_uuid_B_D(self):
        df_links = pd.read_csv("data\\burgerLinker\\output\\raw\\within-B-D-maxLev-3.csv", sep=",")
        
        for link in df_links.itertuples():
            persons = self.df_births[self.df_births["id_registration"] == link.id_certificate_newborn]
            child = persons[persons["role"] == 1].iloc[0]["uuid"]

            persons = self.df_deaths[self.df_deaths["id_registration"] == link.id_certificate_deceased]
            deceased = persons[persons["role"] == 10].iloc[0]["uuid"]

            self.links.append([5, child, deceased, "c"])

            break


    def save_links(self):
        df_links = pd.DataFrame(self.links, columns=[
            "mode",
            "reference_uuid",
            "link_uuid", 
            "sex"])

        path_result_persons = unique_file_name(f"results\\burgerLinker\\BL Links Persons", "csv")
        df_links.to_csv(path_result_persons, sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        print(re.sub(" +", " ", f"""
            -------------------------------------
            Saved person links at {path_result_persons}
        """))


persons = GeneratePersonLinks()
persons.get_uuid_B_M()
persons.get_uuid_D_M()
persons.get_uuid_M_M()
persons.get_uuid_B_D()
persons.save_links()

