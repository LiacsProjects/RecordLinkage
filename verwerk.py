import Levenshtein
import polars as pl
import csv
import os
import re
from datetime import date

INDEX_BRUIDEGOM = 29
INDEX_BRUIDEGOM_VADER = 47
INDEX_BRUIDEGOM_MOEDER = 65
INDEX_BRUID = 83
INDEX_BRUID_VADER = 101
INDEX_BRUID_MOEDER = 119
INDEX_KIND = 28
INDEX_VADER = 47
INDEX_MOEDER = 66

ROLLEN = {
    "Bruidegom": INDEX_BRUIDEGOM,
    "Vader bruidegom": INDEX_BRUIDEGOM_VADER,
    "Moeder bruidegom": INDEX_BRUIDEGOM_MOEDER,
    "Bruid": INDEX_BRUID,
    "Vader bruid": INDEX_BRUID_VADER,
    "Moeder bruid": INDEX_BRUID_MOEDER,
}


def clean(value: str):
    value = str(value).replace("<NA>", "").strip()
    return value if value else None


def get_date(datum: str) -> tuple[int, int, int]:

    def keep_numeric(text: str):
        return int("".join([ch for ch in text if ch.isnumeric()]))

    date_list = datum.split("-")
    if datum[2] == "-":
        index_day, index_month, index_year = 0, 1, 2
    else:
        index_day, index_month, index_year = 2, 1, 0

    dag = keep_numeric(date_list[index_day])
    maand = keep_numeric(date_list[index_month])
    jaar = keep_numeric(date_list[index_year])

    if dag < 0 or dag > 31:
        dag = None
    if maand < 0 or maand > 12:
        maand = None
    if jaar < 1700 or jaar > 1999:
        jaar = None
    return jaar, maand, dag


def get_age(age_raw: str):
    try:
        age = ''
        for ch in age_raw:
            if ch.isnumeric():
                age += ch

        if len(age) > 0:
            return int(age)
        else:
            return None
    except Exception:
        return None


def generate_persons_marriage():
    df_huwelijken_ruw = pl.read_csv(
        "data\\elo\\Huwelijk.csv",
        separator=";",
    )
    personen = []
    relaties = []
    huwelijken = []

    # aantal_incorrecte_datum = 0

    for huwelijk in df_huwelijken_ruw.iter_rows():
        try:
            datum_huwelijk = get_date(huwelijk[26])
        except Exception:
            continue

        huwelijken.append([
            huwelijk[0],
            datum_huwelijk,
            huwelijk[INDEX_BRUIDEGOM],
            huwelijk[INDEX_BRUID],
        ])

        for rol in ROLLEN:
            index = ROLLEN[rol]

            if not huwelijk[index]:
                continue

            try:
                dag, maand, jaar = get_date(huwelijk[index + 15])
            except Exception:
                dag, maand, jaar = None, None, None

            leeftijd = get_age(clean(huwelijk[index + 12]))

            if not jaar and leeftijd:
                jaar = datum_huwelijk[0] - leeftijd

            persoon = [
                huwelijk[index],                # uuid
                rol,                            # Role
                clean(huwelijk[index + 9]),     # Voornaam
                clean(huwelijk[index + 10]),    # Tussenvoegsel
                clean(huwelijk[index + 11]),    # Geslachtsnaam
                leeftijd,                       # Age
                clean(huwelijk[index + 13]),    # Beroep
                clean(huwelijk[index + 16]),    # Woonplaats
                clean(huwelijk[index + 14]),    # Geboorte plaats
                jaar, maand, dag,               # Geboorte datum
            ]
            personen.append(persoon)

        if huwelijk[INDEX_BRUIDEGOM] and huwelijk[INDEX_BRUID]:
            relaties.append([
                huwelijk[INDEX_BRUIDEGOM],
                huwelijk[INDEX_BRUID],
                "Partner"
            ])
        if huwelijk[INDEX_BRUIDEGOM] and huwelijk[INDEX_BRUIDEGOM_VADER]:
            relaties.append([
                huwelijk[INDEX_BRUIDEGOM],
                huwelijk[INDEX_BRUIDEGOM_VADER],
                "Vader"
            ])
        if huwelijk[INDEX_BRUIDEGOM] and huwelijk[INDEX_BRUIDEGOM_MOEDER]:
            relaties.append([
                huwelijk[INDEX_BRUIDEGOM],
                huwelijk[INDEX_BRUIDEGOM_MOEDER],
                "Moeder"
            ])
        if huwelijk[INDEX_BRUID] and huwelijk[INDEX_BRUID_VADER]:
            relaties.append([
                huwelijk[INDEX_BRUID],
                huwelijk[INDEX_BRUID_VADER],
                "Vader"
            ])
        if huwelijk[INDEX_BRUID] and huwelijk[INDEX_BRUID_MOEDER]:
            relaties.append([
                huwelijk[INDEX_BRUID],
                huwelijk[INDEX_BRUID_MOEDER],
                "Moeder"
            ])

    print(len(huwelijken))
    print(len(personen))
    print(len(relaties))

    df_huwelijken = pl.DataFrame(
        huwelijken,
        orient="row",
        schema=[
            "uuid",
            "datum",
            "bruidegom-uuid",
            "bruid-uuid",
        ]
    )
    df_huwelijken.write_parquet("data\\huwelijken.pq")

    df_personen = pl.DataFrame(
        personen,
        orient="row",
        schema=[
            "uuid",
            "rol",
            "voornaam",
            "tussenvoegsel",
            "geslachtsnaam",
            "leeftijd",
            "beroep",
            "woonplaats",
            "geboorteplaats",
            "geboortejaar",
            "geboortemaand",
            "geboortedag",
        ]
    )
    df_personen
    df_personen.write_parquet("data\\personen.pq")

    df_relaties = pl.DataFrame(
        relaties,
        orient="row",
        schema=[
            "rel1-uuid",
            "rel2-datum",
            "relatie",
        ]
    )
    df_relaties.write_parquet("data\\relaties.pq")


if __name__ == "__main__":
    generate_persons_marriage()
