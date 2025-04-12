import polars as pl


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
    "Kind": INDEX_KIND,
    "Vader": INDEX_VADER,
    "Moeder": INDEX_MOEDER,
}


def opschonen(value: str):
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


def verwerk_geboorten():
    df_geboorten_ruw = pl.read_csv(
        "data\\elo\\Geboorte.csv",
        separator=";",
        ignore_errors=True,
    )
    personen = []
    relaties = []
    geboorten = []
    aantal = 0
    aantal_missende_geb = {rol: 0 for rol in ROLLEN}
    aantal_missende_persoon = {rol: 0 for rol in ROLLEN}
    for geboorte in df_geboorten_ruw.iter_rows():

        try:
            datum_geboorte = get_date(geboorte[42])
        except Exception as e:
            aantal += 1
            # print(e, "datum geboorte")
            # breakpoint()
            # print(geboorte)
            # breakpoint()
            continue

        geboorten.append([
            geboorte[0],
            *datum_geboorte,
            geboorte[INDEX_KIND],
        ])
        for rol in ROLLEN:
            index = ROLLEN[rol]

            if not geboorte[index]:
                aantal_missende_persoon[rol] += 1
                # print("niks")
                # breakpoint()
                continue

            try:
                jaar, maand, dag = get_date(geboorte[index + 14])
            except Exception as e:
                aantal_missende_geb[rol] += 1
                # print(e, "geboortedatum")
                # breakpoint()
                jaar, maand, dag = None, None, None

            leeftijd = get_age(opschonen(geboorte[index + 17]))

            if not jaar and leeftijd:
                jaar = datum_geboorte[0] - leeftijd

            persoon = [
                geboorte[index],                         # uuid
                rol,                                               # Role
                opschonen(geboorte[index + 9]),              # Voornaam
                opschonen(geboorte[index + 10]),             # Tussenvoegsel
                opschonen(geboorte[index + 11]),             # Geslachtsnaam
                leeftijd,    # Age
                opschonen(geboorte[index + 16]),             # Beroep
                opschonen(geboorte[index + 13]),             # Geboorte plaats
                jaar, maand, dag,                 # Geboorte datum
                opschonen(geboorte[index + 12])]             # Woonplaats

            personen.append(persoon)

        if geboorte[INDEX_VADER] and geboorte[INDEX_MOEDER]:
            relaties.append([
                geboorte[INDEX_VADER],
                geboorte[INDEX_MOEDER],
                "Partner"
            ])
        if geboorte[INDEX_KIND] and geboorte[INDEX_VADER]:
            relaties.append([
                geboorte[INDEX_KIND],
                geboorte[INDEX_VADER],
                "Vader"
            ])
        if geboorte[INDEX_KIND] and geboorte[INDEX_MOEDER]:
            relaties.append([
                geboorte[INDEX_KIND],
                geboorte[INDEX_MOEDER],
                "Moeder"
            ])
        # break
    print(len(geboorten))
    print(len(personen))
    print(len(relaties))
    breakpoint()

    df_geboorten = pl.DataFrame(
        geboorten,
        orient="row",
        schema=[
            "uuid",
            "jaar", "maand", "dag",
            "bruidegom-uuid",
            "bruid-uuid",
        ]
    )
    df_geboorten.write_parquet("data\\geboorten.pq")

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
    verwerk_geboorten()
