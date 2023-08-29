import pandas as pd
import csv
import os
import unidecode


WHITELIST = set("abcdefghijklmnopqrstuvwxyz")

PAIRS = {"birth": {
            1: {"pair": ["father", "mother"], "child": "child", "age": None}},
         "marriage": {
            2: {"pair": ["groom", "bride"], "child": None, "age": "bride"},
            3: {"pair": ["groom_father", "groom_mother"], "child": "groom", "age": "groom"},
            4: {"pair": ["bride_father", "bride_mother"], "child": "bride", "age": "bride"}},
         "death": {
            5: {"pair": ["deceased", "deceased_partner"], "child": None, "age": None},
            6: {"pair": ["deceased_father", "deceased_mother"], "child": "deceased", "age": None}}}

INDEXES = {"child": 29,
           "father": 48,
           "mother": 67,
           "groom": 30,
           "groom_father": 48,
           "groom_mother": 66,
           "bride": 84,
           "bride_father": 102,
           "bride_mother": 120,
           "deceased": 29,
           "deceased_partner": 48,
           "deceased_father": 68,
           "deceased_mother": 87}


def unique_file_name(path, extension = ""):
    i = 0
    temp_path = path
    while os.path.exists(temp_path + "." + extension):  #check of het bestand al bestaat
        i += 1
        temp_path = path + " ({})".format(str(i))
    return temp_path + "." + extension


class GeneratePairs():
    def __init__(self):
        # Read files
        self.certificates = {"birth": pd.read_csv("data\\unprocessed\\Geboorte.csv", sep=";", dtype="string"),
                             "marriage": pd.read_csv("data\\unprocessed\\Huwelijk.csv", sep=";", dtype="string"),
                             "death": pd.read_csv("data\\unprocessed\\Overlijden.csv", sep=";", dtype="string")}

        self.exceptions = []
        self.pairs = []
        self.processed_before = 0


    def get_date(self, date:str):

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
            return 0, 0, 0


    def get_age(self, age_raw:str):
        try:
            age = ''
            for ch in age_raw:
                if ch.isnumeric():  
                    age += ch

            if len(age) > 0:
                return int(age)
            else:
                return -1
        except Exception as e:
            return -1
        

    def get_name(self, first_name, last_name):

        def clean(chars):
            if isinstance(chars, str):
                chars = str(chars).lower()
                chars = unidecode.unidecode(chars)
                chars = "".join(filter(WHITELIST.__contains__, chars))
                chars = chars.replace("ch", "g").replace("c", "k").replace("z", "s").replace("ph", "f").replace("ij", "y")
                return chars

        first_names = "".join(sorted([clean(firstname) for firstname in first_name.split()]))
        last_name = clean(last_name)

        return first_names + last_name, last_name[0]
    

    def get_pairs(self, cert_type):
        self.processed_before = len(self.pairs) - self.processed_before
        
        for cert in self.certificates[cert_type].itertuples():
            uuid = cert[1]

            if cert_type == "birth":
                _, _, year = self.get_date(cert[INDEXES["child"] + 14])
            elif cert_type == "marriage":
                _, _, year = self.get_date(cert[27])
            elif cert_type == "death":
                _, _, year = self.get_date(cert[INDEXES["deceased"] + 14])


            for pair in PAIRS[cert_type]:
                try:
                    index_man = INDEXES[PAIRS[cert_type][pair]["pair"][0]]
                    index_woman = INDEXES[PAIRS[cert_type][pair]["pair"][1]]

                    man, letter_man = self.get_name(cert[index_man + 9], cert[index_man + 11])
                    woman, letter_woman = self.get_name(cert[index_woman + 9], cert[index_woman + 11])
                    
                    try:
                        index_child = INDEXES[PAIRS[cert_type][pair]["child"]]
                        child, _ = self.get_name(cert[index_child + 9], cert[index_child + 11])
                        child_uuid = cert[index_child]
                    except:
                        child = ""
                        child_uuid = ""

                    try:
                        age = self.get_age(cert[INDEXES[PAIRS[cert_type][pair]["age"]] + 12])
                    except:
                        age = -1

                    pair = [year,
                            letter_man + letter_woman, 
                            pair, 
                            man, 
                            woman, 
                            child, 
                            age, 
                            uuid, 
                            cert[index_man], 
                            cert[index_woman],
                            child_uuid]
                    
                    self.pairs.append(pair)

                except Exception as e:
                    self.exceptions.append([pair, uuid, e])


    def construct_pairs(self):
        self.get_pairs("birth")

        print(f"""
        Pairs birth processed. Total: {len(self.pairs) - self.processed_before}
        ---------------------------------------

        """)

        self.get_pairs("marriage")

        print(f"""
        Pairs marriage processed. Total: {len(self.pairs) - self.processed_before}
        ---------------------------------------

        """)


        self.get_pairs("death")

        print(f"""
        Pairs death processed. Total: {len(self.pairs) - self.processed_before}
        ---------------------------------------

        """)

        df_pairs = pd.DataFrame(self.pairs, columns=[
            "year", 
            "first_letters", 
            "pair",  
            "man", 
            "woman", 
            "child", 
            "age", 
            "uuid", 
            "man_uuid",
            "woman_uuid",
            "child_uuid"])

        df_exceptions = pd.DataFrame(self.exceptions, columns=[
            "pair",
            "cert_uuid", 
            "exception"])
        
        # df_links['first_letters'].value_counts().to_csv("distr.csv", sep=";", quoting=csv.QUOTE_NONNUMERIC)
        df_exceptions.to_csv(unique_file_name("RecordLinker\\data\\exceptions", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
        df_pairs.to_csv(unique_file_name("RecordLinker\\data\\pairs", "csv"), sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)

        print("All pairs processed. Total:", len(df_pairs.index))
        print("Exceptions:", len(df_exceptions.index))


if __name__ == '__main__':
    pairs = GeneratePairs()
    pairs.construct_pairs()

