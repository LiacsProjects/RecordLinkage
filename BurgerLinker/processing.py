import Levenshtein
import pandas as pd
import csv
import os
import re


def unique_file_name(path, extension = ""):
    i = 0
    temp_path = path
    while os.path.exists(temp_path + "." + extension):  #check of het bestand al bestaat
        i += 1
        temp_path = path + " ({})".format(str(i))
    return temp_path + "." + extension


class GeneratePersonLinks():
    def __init__(self):
        self.df_births = pd.read_csv("BurgerLinker\\input\\Births\\persons.csv", sep=";")
        self.df_marriage = pd.read_csv("BurgerLinker\\input\\Marriages\\persons.csv", sep=";")
        self.df_deaths = pd.read_csv("BurgerLinker\\input\\Deaths\\persons.csv", sep=";")
        self.links = []


    def get_uuid_B_M(self):
        """
        For each linked marriage and birth certificate, find the linked person uuids
        """
        df_links = pd.read_csv("BurgerLinker\\output\\within-B-M-maxLev-3.csv", sep=",")

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


        df_links = pd.read_csv("BurgerLinker\\output\\between-B-M-maxLev-3.csv", sep=",")

        for link in df_links.itertuples():
            persons = self.df_births[self.df_births["id_registration"] == link.id_certificate_newbornParents]
            father = persons[persons["role"] == 3].iloc[0]["uuid"]
            mother = persons[persons["role"] == 2].iloc[0]["uuid"]

            persons = self.df_marriage[self.df_marriage["id_registration"] == link.id_certificate_partners]
            groom = persons[persons["role"] == 7].iloc[0]["uuid"]
            bride = persons[persons["role"] == 4].iloc[0]["uuid"]

            self.links.append([2, father, groom, "m"])
            self.links.append([2, mother, bride, "v"])


    def get_uuid_D_M(self):
        """
        For each linked marriage and death certificate, find the linked person uuids
        """
        df_links = pd.read_csv("BurgerLinker\\output\\between-D-M-maxLev-3.csv", sep=",")

        for link in df_links.itertuples():
            persons = self.df_marriage[self.df_marriage["id_registration"] == link.id_certificate_partners]
            groom = persons[persons["role"] == 7].iloc[0]["uuid"]
            bride = persons[persons["role"] == 4].iloc[0]["uuid"]

            persons = self.df_deaths[self.df_deaths["id_registration"] == link.id_certificate_deceasedParents]
            father = persons[persons["role"] == 3].iloc[0]["uuid"]
            mother = persons[persons["role"] == 2].iloc[0]["uuid"]

            self.links.append([3, father, groom, "m"])
            self.links.append([3, mother, bride, "v"])


    def get_uuid_M_M(self):
        """
        For each linked marriage certificates, find the linked person uuids
        """
        df_links = pd.read_csv("BurgerLinker\\output\\between-M-M-maxLev-3.csv", sep=",")

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


    def get_uuid_B_D(self):
        """
        For each linked birth and death certificate, find the linked person uuids
        """
        df_links = pd.read_csv("BurgerLinker\\output\\within-B-D-maxLev-3.csv", sep=",")
        
        for link in df_links.itertuples():
            persons = self.df_births[self.df_births["id_registration"] == link.id_certificate_newborn]
            child = persons[persons["role"] == 1].iloc[0]["uuid"]

            persons = self.df_deaths[self.df_deaths["id_registration"] == link.id_certificate_deceased]
            deceased = persons[persons["role"] == 10].iloc[0]["uuid"]

            self.links.append([5, child, deceased, "c"])


    def save_links(self):
        """
        Saving person links to .csv
        """
        df_links = pd.DataFrame(self.links, columns=[
            "mode",
            "reference_uuid",
            "link_uuid", 
            "sex"])

        path_result_persons = unique_file_name(f"BurgerLinker\\results\\BL Links Persons", "csv")
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

