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
    return str(string).replace("<NA>", "").lower().replace("ch", "g").replace("c", "k").replace("z", "s").replace("ph", "f").replace("ij", "y").replace("\\", "").strip()


def generate_persons():
    df_geboortes = pd.read_csv(r'data\unprocessed\Geboorte.csv', sep=";", dtype="string")

    person_id = 1000001
    persons = []

    registration_id = 1000001
    registrations = []
    for geboorte in df_geboortes.iterrows():

        try:
            registration_day, registration_month, registration_year = get_date(str(geboorte[1]["Kind-Datum geboorte"]).replace("<NA>", "").strip())
            
            registrations.append([
                registration_id,
                1,
                "g",
                None,
                registration_day,
                registration_month,
                registration_year,
                str(geboorte[1]["uuid"]).strip()])
        
            try:
                # Kind
                persons.append([
                    person_id,
                    registration_id,
                    1,
                    get_clean_string(geboorte[1]["Kind-Voornaam"]),
                    get_clean_string(geboorte[1]["Kind-Tussenvoegsel"]),
                    get_clean_string(geboorte[1]["Kind-Geslachtsnaam"]),
                    None,
                    None,
                    1,
                    None,
                    None,
                    None,
                    None,
                    0,
                    None,
                    1,
                    registration_day,
                    registration_month,
                    registration_year,
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
                age_day, age_week, age_month, age_year = get_age(str(geboorte[1]["Moeder-Leeftijd"]).replace("<NA>", "").lower().strip())
                # Moeder
                persons.append([
                    person_id,
                    registration_id,
                    1,
                    get_clean_string(geboorte[1]["Moeder-Voornaam"]),
                    get_clean_string(geboorte[1]["Moeder-Tussenvoegsel"]),
                    get_clean_string(geboorte[1]["Moeder-Geslachtsnaam"]),
                    "f",
                    None,
                    2,
                    get_clean_string(geboorte[1]["Moeder-Beroep"]),
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
                age_day, age_week, age_month, age_year = get_age(str(geboorte[1]["Vader-Leeftijd"]).replace("<NA>", "").lower().strip())
                # Vader
                persons.append([
                    person_id,
                    registration_id,
                    1,
                    get_clean_string(geboorte[1]["Vader-Voornaam"]),
                    get_clean_string(geboorte[1]["Vader-Tussenvoegsel"]),
                    get_clean_string(geboorte[1]["Vader-Geslachtsnaam"]),
                    "m",
                    None,
                    3,
                    get_clean_string(geboorte[1]["Vader-Beroep"]),
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
                print("Person not added:", geboorte)

        except Exception as e:
            print("Registration not added:", geboorte[1]["uuid"], e)

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

    df_registrations.to_csv(r"data\burgerLinker\registrations b.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)
    df_persons.to_csv(r"data\burgerLinker\persons b.csv", sep=";", index=False, quoting=csv.QUOTE_NONNUMERIC)


generate_persons()

