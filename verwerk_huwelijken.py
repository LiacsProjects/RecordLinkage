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
    "Bruidegom": INDEX_BRUIDEGOM,
    "Vader bruidegom": INDEX_BRUIDEGOM_VADER,
    "Moeder bruidegom": INDEX_BRUIDEGOM_MOEDER,
    "Bruid": INDEX_BRUID,
    "Vader bruid": INDEX_BRUID_VADER,
    "Moeder bruid": INDEX_BRUID_MOEDER,
}

GESLACHT = {
    "Bruidegom": "m",
    "Vader bruidegom": "m",
    "Moeder bruidegom": "v",
    "Bruid": "v",
    "Vader bruid": "m",
    "Moeder bruid": "v",
}


def opschonen(value: str):
    value = str(value).replace("<NA>", "").strip()
    return value if value else None


def get_date(datum: str) -> tuple[int, int, int]:

    def keep_numeric(text: str):
        return int("".join([ch for ch in text if ch.isnumeric()]))

    date_list = datum.replace("!", "1").split("-")
    if datum[2] == "-":
        index_day, index_month, index_year = 0, 1, 2
    else:
        index_day, index_month, index_year = 2, 1, 0

    dag = keep_numeric(date_list[index_day])
    maand = keep_numeric(date_list[index_month])
    jaar = keep_numeric(date_list[index_year])

    if dag < 1 or dag > 31:
        dag = None
    if maand < 1 or maand > 12:
        maand = None
    if jaar < 1500 or jaar > 1999:
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

    aantal = 0
    aantal_missende_geb = {rol: 0 for rol in ROLLEN}
    aantal_missende_persoon = {rol: 0 for rol in ROLLEN}

    for huwelijk in df_huwelijken_ruw.iter_rows():
        try:
            datum_huwelijk = get_date(huwelijk[26])
        except Exception:
            aantal += 1
            continue

        huwelijken.append([
            huwelijk[0],
            *datum_huwelijk,
            huwelijk[INDEX_BRUIDEGOM],
            huwelijk[INDEX_BRUID],
        ])

        for rol in ROLLEN:
            index = ROLLEN[rol]

            if not huwelijk[index]:
                aantal_missende_persoon[rol] += 1
                continue

            try:
                jaar, maand, dag = get_date(huwelijk[index + 15])
            except Exception:
                aantal_missende_geb[rol] += 1
                jaar, maand, dag = None, None, None

            if jaar:
                leeftijd = datum_huwelijk[0] - jaar
                leeftijd_veld = get_age(opschonen(huwelijk[index + 12]))

                if leeftijd_veld:
                    if (
                        leeftijd > leeftijd_veld - 1
                        and leeftijd < leeftijd_veld + 1
                    ):
                        leeftijd = leeftijd_veld
            else:
                leeftijd = get_age(opschonen(huwelijk[index + 12]))
                if leeftijd:
                    jaar = datum_huwelijk[0] - leeftijd

            persoon = [
                huwelijk[index],                    # uuid
                rol,                                # Rol
                opschonen(huwelijk[index + 9]),     # Voornaam
                opschonen(huwelijk[index + 10]),    # Tussenvoegsel
                opschonen(huwelijk[index + 11]),    # Geslachtsnaam
                leeftijd,                           # Leeftijd
                GESLACHT[rol],                      # Geslacht
                opschonen(huwelijk[index + 13]),    # Beroep
                opschonen(huwelijk[index + 16]),    # Woonplaats
                opschonen(huwelijk[index + 14]),    # Geboorte plaats
                jaar, maand, dag,                   # Geboorte datum
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
        if (
            huwelijk[INDEX_BRUIDEGOM_VADER]
            and huwelijk[INDEX_BRUIDEGOM_MOEDER]
        ):
            relaties.append([
                huwelijk[INDEX_BRUIDEGOM_VADER],
                huwelijk[INDEX_BRUIDEGOM_MOEDER],
                "Partner"
            ])
        if huwelijk[INDEX_BRUID_VADER] and huwelijk[INDEX_BRUID_MOEDER]:
            relaties.append([
                huwelijk[INDEX_BRUID_VADER],
                huwelijk[INDEX_BRUID_MOEDER],
                "Partner"
            ])

    print(aantal)
    print(aantal_missende_geb)
    print(aantal_missende_persoon)

    print(len(huwelijken))
    print(len(personen))
    print(len(relaties))

    df_huwelijken = pl.DataFrame(
        huwelijken,
        orient="row",
        schema=[
            "uuid",
            "jaar", "maand", "dag",
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
            "geslacht",
            "beroep",
            "woonplaats",
            "geboorteplaats",
            "geboortejaar",
            "geboortemaand",
            "geboortedag",
        ]
    )
    df_personen
    df_personen.write_parquet("data\\hw-personen.pq")

    df_relaties = pl.DataFrame(
        relaties,
        orient="row",
        schema=[
            "rel1-uuid",
            "rel2-datum",
            "relatie",
        ]
    )
    df_relaties.write_parquet("data\\hw-relaties.pq")


if __name__ == "__main__":
    generate_persons_marriage()
