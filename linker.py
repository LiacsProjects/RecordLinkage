import polars as pl
import Levenshtein


MAX_LEVENSTHEIN = 3

AGE_MARRIED_RANGE = {
    "min": 15,
    "max": 80}

AGE_MOTHER_RANGE = {
    "min": 15,
    "max": 50}

AGE_DEATH_RANGE = {
    "min": 0,
    "max": 100}

MODES = {
    1: {"references": [1], "potential_links": [2, 3]},  # 1
    2: {"references": [1], "potential_links": [4]},  # 2
    3: {"references": [1], "potential_links": [5]},
    4: {"references": [1], "potential_links": [6]},

    5: {"references": [2, 3], "potential_links": [2, 3]},
    6: {"references": [2, 3], "potential_links": [4]},  # 3
    7: {"references": [2, 3], "potential_links": [5]},
    8: {"references": [2, 3], "potential_links": [6]},  # 5

    9: {"references": [4], "potential_links": [4]},  # 4
    10: {"references": [4], "potential_links": [5]},
    11: {"references": [4], "potential_links": [6]},  # 6

    12: {"references": [5], "potential_links": [5]},
    13: {"references": [5], "potential_links": [6]},

    14: {"references": [6], "potential_links": [6]},
}


def main():
    personen = pl.concat([
        pl.read_parquet("data\\hw-personen.pq"),
        pl.read_parquet("data\\gb-personen.pq"),
    ])
    links = set()
    type_filter = {"dag": 0, "maand": 0, "jaar": 0, "overig": 0}
    print(personen.shape)

    i = 0
    for persoon in personen.iter_rows():
        selectie = None
        i += 1
        if i % 10_000 == 0:
            # if i > 100_000:
            #     break
            # break
            print(i, len(links), type_filter)

        if persoon[10] and persoon[11] and persoon[12]:
            type_filter["dag"] += 1

            selectie = (
                (pl.col("geslacht") == persoon[6] if persoon[6] else True)
                & (pl.col("geboortejaar") == persoon[10])  # if persoon[10] else (True)
                & (pl.col("geboortedag") == persoon[12])  # if persoon[6] else (True)
                & (pl.col("geboortemaand") == persoon[11])  # if persoon[6] else (True)
            )

        elif persoon[10] and persoon[11]:
            type_filter["maand"] += 1
            selectie = (
                (pl.col("geslacht") == persoon[6] if persoon[6] else True)
                & (pl.col("geboortejaar") == persoon[10])  # if persoon[10] else (True)
                & (pl.col("geboortemaand") == persoon[11])  # if persoon[6] else (True)
            )
        elif persoon[10]:
            type_filter["jaar"] += 1
            selectie = (
                (pl.col("geslacht") == persoon[6] if persoon[6] else True)
                & (pl.col("geboortejaar") == persoon[10])  # if persoon[10] else (True)
            )
        else:
            type_filter["overig"] += 1
        if selectie is None:
            continue

        mogelijke_links = personen.filter(selectie)
        if mogelijke_links.is_empty():
            continue

        try:
            naam: str = persoon[2] + persoon[4]
            naam = naam.lower().strip()
        except Exception:
            # print(persoon[2], persoon[4])
            continue
        # print(naam)
        # print(persoon)
        # print(mogelijke_links)
        # break
        for mogelijke_link in mogelijke_links.iter_rows():
            if persoon[0] == mogelijke_link[0]:
                continue
            # if frozenset([persoon[0], mogelijke_link[0]]) in links:
            #     continue

            try:
                naam2: str = mogelijke_link[2] + mogelijke_link[4]
                naam2 = naam2.lower().strip()
            except Exception:
                # print(persoon[2], persoon[4])
                continue
            afstand = Levenshtein.distance(naam, naam2)
            # breakpoint()
            if afstand <= MAX_LEVENSTHEIN:
                links.add(frozenset([persoon[0], mogelijke_link[0]]))

    print(type_filter)
    print(len(links))
    print(list(links)[:10])
    # breakpoint()
    with open("data\\resultaat\\links.csv", "w") as res:
        for link in links:
            res.write(";".join(link) + "\n")


if __name__ == "__main__":
    main()
