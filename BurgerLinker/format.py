import pandas as pd
import csv


def get_date(date:str):
    date_list = date.split("-")
    if date[2] == "-":
        return date_list[0], date_list[1], date_list[2]
    else:
        return date_list[2], date_list[1], date_list[0]


def get_age(age:str):
    # try:
    #     almost = False
    #     age_parts = age.split()
    #     if len(age_parts) == 1 and age:
    #         age_year = int(age)

    #     else:
    #         for index, part in enumerate(age_parts):
    #             if "jaar" in part or "jaren" in part:
    #                 age_year = int(age_parts[index - 1])
    #                 if almost:
    #                     age_year -= 1
    #                     almost = False
    #             elif "maand" in part:
    #                 age_month = int(age_parts[index - 1])
    #                 if almost:
    #                     age_month -= 1
    #                     almost = False
    #             elif "week" in part or "weken" in part:
    #                 age_week = int(age_parts[index - 1])
    #                 if almost:
    #                     age_week -= 1
    #                     almost = False
    #             elif "dag" in part:
    #                 age_day = int(age_parts[index - 1])
    #                 if almost:
    #                     age_day -= 1
    #                     almost = False
    #             elif "bijna" in part:
    #                 almost = True
        
    # except Exception as e:
    #     print(e)
    age_day = None
    age_week = None
    age_month = None
    age_year = None

    years = ''
    for ch in age:
        if ch.isnumeric():  
            years += ch

    if len(years) > 0:
        age_year = int(years)

    return age_day, age_week, age_month, age_year


def get_clean_string(string):
    return str(string).replace("<NA>", "").lower().replace("ch", "g").replace("c", "k").replace("z", "s").replace("ph", "f").replace("ij", "y").strip()


def generate_persons():
    # df_geboorte = pd.read_csv(r'data\geboorte.csv', sep=";", dtype="string")
    df_huwelijk = pd.read_csv(r'data\unprocessed\Huwelijk.csv', sep=";", dtype="string")
    # df_scheiding = pd.read_csv(r'data\echtscheiding.csv', sep=";") 
    # df_overlijden = pd.read_csv(r'data\overlijden.csv', sep=";", dtype="string")

    person_id = 1
    persons = []

    registration_id = 1
    registrations = []
    for huwelijk in df_huwelijk.iterrows():
        try:
            registration_day, registration_month, registration_year = get_date(str(huwelijk[1]["Datum"]).replace("<NA>", "").strip())
            
            registrations.append([
                registration_id,
                2,
                "h",
                None,
                registration_day,
                registration_month,
                registration_year,
                str(huwelijk[1]["uuid"]).strip()])

            try:
                age_day, age_week, age_month, age_year = get_age(str(huwelijk[1]["Bruid-Leeftijd"]).replace("<NA>", "").lower().strip())
                # Bruid
                persons.append([
                    person_id,
                    registration_id,
                    2,
                    get_clean_string(huwelijk[1]["Bruid-Voornaam"]),
                    get_clean_string(huwelijk[1]["Bruid-Tussenvoegsel"]),
                    get_clean_string(huwelijk[1]["Bruid-Geslachtsnaam"]),
                    "f",
                    None,
                    4,
                    get_clean_string(huwelijk[1]["Bruid-Beroep"]),
                    age_day,
                    age_week,
                    age_month,
                    age_year,
                    None,
                    0,
                    0,
                    0,
                    0,
                    None,
                    'a',
                    None,
                    0,
                    0,
                    0,
                    0,
                    None,
                    f"{str(registration_day)}-{str(registration_month)}-{str(registration_year)}",
                    1,
                    registration_day,
                    registration_month,
                    registration_year,
                    None
                ])

                person_id +=1
                age_day, age_week, age_month, age_year = get_age(str(huwelijk[1]["Moeder bruid-Leeftijd"]).replace("<NA>", "").lower().strip())
                # Moeder bruid
                persons.append([
                    person_id,
                    registration_id,
                    2,
                    get_clean_string(huwelijk[1]["Moeder bruid-Voornaam"]),
                    get_clean_string(huwelijk[1]["Moeder bruid-Tussenvoegsel"]),
                    get_clean_string(huwelijk[1]["Moeder bruid-Geslachtsnaam"]),
                    "f",
                    None,
                    5,
                    get_clean_string(huwelijk[1]["Moeder bruid-Beroep"]),
                    age_day,
                    age_week,
                    age_month,
                    age_year,
                    None,
                    0,
                    0,
                    0,
                    0,
                    None,
                    'a',
                    None,
                    0,
                    0,
                    0,
                    0,
                    None,
                    None,
                    0,
                    0,
                    0,
                    0,
                    None
                ])

                person_id +=1            
                age_day, age_week, age_month, age_year = get_age(str(huwelijk[1]["Vader bruid-Leeftijd"]).replace("<NA>", "").lower().strip())
                # Vader bruid
                persons.append([
                    person_id,
                    registration_id,
                    2,
                    get_clean_string(huwelijk[1]["Vader bruid-Voornaam"]),
                    get_clean_string(huwelijk[1]["Vader bruid-Tussenvoegsel"]),
                    get_clean_string(huwelijk[1]["Vader bruid-Geslachtsnaam"]),
                    "m",
                    None,
                    6,
                    get_clean_string(huwelijk[1]["Vader bruid-Beroep"]),
                    age_day,
                    age_week,
                    age_month,
                    age_year,
                    None,
                    0,
                    0,
                    0,
                    0,
                    None,
                    'a',
                    None,
                    0,
                    0,
                    0,
                    0,
                    None,
                    None,
                    0,
                    0,
                    0,
                    0,
                    None
                ])

                person_id +=1
                age_day, age_week, age_month, age_year = get_age(str(huwelijk[1]["Bruidegom-Leeftijd"]).replace("<NA>", "").lower().strip())
                # Bruidegom
                persons.append([
                    person_id,
                    registration_id,
                    2,
                    get_clean_string(huwelijk[1]["Bruidegom-Voornaam"]),
                    get_clean_string(huwelijk[1]["Bruidegom-Tussenvoegsel"]),
                    get_clean_string(huwelijk[1]["Bruidegom-Geslachtsnaam"]),
                    "m",
                    None,
                    7,
                    get_clean_string(huwelijk[1]["Bruidegom-Beroep"]),
                    age_day,
                    age_week,
                    age_month,
                    age_year,
                    None,
                    0,
                    0,
                    0,
                    0,
                    None,
                    'a',
                    None,
                    0,
                    0,
                    0,
                    0,
                    None,
                    f"{str(registration_day)}-{str(registration_month)}-{str(registration_year)}",
                    1,
                    registration_day,
                    registration_month,
                    registration_year,
                    None
                ])

                person_id +=1
                age_day, age_week, age_month, age_year = get_age(str(huwelijk[1]["Moeder bruidegom-Leeftijd"]).replace("<NA>", "").lower().strip())
                # Moeder bruidegom
                persons.append([
                    person_id,
                    registration_id,
                    2,
                    get_clean_string(huwelijk[1]["Moeder bruidegom-Voornaam"]),
                    get_clean_string(huwelijk[1]["Moeder bruidegom-Tussenvoegsel"]),
                    get_clean_string(huwelijk[1]["Moeder bruidegom-Geslachtsnaam"]),
                    "f",
                    None,
                    8,
                    get_clean_string(huwelijk[1]["Moeder bruidegom-Beroep"]),
                    age_day,
                    age_week,
                    age_month,
                    age_year,
                    None,
                    0,
                    0,
                    0,
                    0,
                    None,
                    'a',
                    None,
                    0,
                    0,
                    0,
                    0,
                    None,
                    None,
                    0,
                    0,
                    0,
                    0,
                    None
                ])

                person_id +=1
                age_day, age_week, age_month, age_year = get_age(str(huwelijk[1]["Vader bruidegom-Leeftijd"]).replace("<NA>", "").lower().strip())
                # Vader bruidegom
                persons.append([
                    person_id,
                    registration_id,
                    2,
                    get_clean_string(huwelijk[1]["Vader bruidegom-Voornaam"]),
                    get_clean_string(huwelijk[1]["Vader bruidegom-Tussenvoegsel"]),
                    get_clean_string(huwelijk[1]["Vader bruidegom-Geslachtsnaam"]),
                    "m",
                    None,
                    9,
                    get_clean_string(huwelijk[1]["Vader bruidegom-Beroep"]),
                    age_day,
                    age_week,
                    age_month,
                    age_year,
                    None,
                    0,
                    0,
                    0,
                    0,
                    None,
                    'a',
                    None,
                    0,
                    0,
                    0,
                    0,
                    None,
                    None,
                    0,
                    0,
                    0,
                    0,
                    None
                ])
                person_id +=1
            except:
                print("Person not added:", huwelijk)

        except:
            print("Registration not added:", huwelijk)

        registration_id += 1

    df_registrations = pd.DataFrame(registrations, columns=["id_registration", 
                                                            "registration_maintype", 
                                                            "registration_type", 
                                                            "registration_location", 
                                                            "registration_day", 
                                                            "registration_month", 
                                                            "registration_year", 
                                                            "registration_seq"])

    df_persons = pd.DataFrame(persons, columns=["id_person",
                                                "id_registration",
                                                "registration_maintype",
                                                "firstname",
                                                "prefix",
                                                "familyname",
                                                "sex",
                                                "civil_status",
                                                "role",
                                                "occupation",
                                                "age_day",
                                                "age_week",
                                                "age_month",
                                                "age_year",
                                                "birth_date",
                                                "birth_date_flag",
                                                "birth_day",
                                                "birth_month",
                                                "birth_year",
                                                "birth_location",
                                                "death",
                                                "stillbirth",
                                                "death_date_flag",
                                                "death_day",
                                                "death_month",
                                                "death_year",
                                                "death_location",
                                                "mar_date",
                                                "mar_date_flag",
                                                "mar_day",
                                                "mar_month",
                                                "mar_year",
                                                "mar_location"])

    df_registrations.to_csv(r"data\burgerLinker\registrations.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
    df_persons.to_csv(r"data\burgerLinker\persons.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


generate_persons()

