# RecordLinker: #
RecordLinker is a novel record linking method. The basic steps to generating Unique Historical Individuals are described below. The process is described in detail afterwards.

1. Preprocessing data in pairs.py
The input data provided by ELO is processed into pairs.

2. Generating links in recordlinker.py
Similar pairs are found by comparing names. The person references in these similar pairs are linked.

3. Processing links to Unique Historical Individuals in "Unique Individuals/individuals.py"
The linked person references are grouped to find all person references that refer to the same person.

# Pairs: #
In pairs.py, the following input files are read and processed:
- Geboorte.csv
- Huwelijk.csv
- Overlijden.csv

These files contain birth, marriage and death certificates. Each certificate mentions people. These people can be divided into pairs. The pairs will descibe a man and a woman. The following types of pairs are possible:
1. father, mother (birth certificate)
2. groom, bride (marriage certificate)
3. father of the groom, mother of the groom (marriage certificate)
4. father of the bride, mother of the bride (marriage certificate)
5. deceased and their partner (death certificate)
6. father of the deceased, mother of the deceased (death certificate)

(The sex of the deceased and their partner is not know. This is important for the order of the name comparison)

Also, for some types of pairs, the name of a child is provided. Children need to be incorporated into the RecordLinker to find the birth certificate of Unique Historical Individuals. The pairs with children become as follows:
1. father, mother, child (birth certificate)
2. groom, bride (no child) (marriage certificate)
3. father of the groom, mother of the groom, groom (marriage certificate)
4. father of the bride, mother of the bride, bride (marriage certificate)
5. deceased and their partner (no child) (death certificate)
6. father of the deceased, mother of the deceased, deceased (death certificate)

The input data contains fields for first name, prefix, last name, age, place of birth, date of birth, occupation, place of residence and comments for each person reference. The names are processed in the following way:
1. Only the first name and last name fields are used (no prefixes)
2. Each first name and last name are cleaned up individually
3. The cleaning up removes capital letters, removes accents and other diacritics, only keeps symbols in the alphabet and replaces
    1. ch for g
    2. c for k
    3. z for s
    4. ph for f
    5. ij for y

4. Orders first names alphabetically and appends the last name (no spaces)

Example:
Mariä Anña van 't Schip
->
annamariasgip

Also, the first letter of the last name is saved (used to optimize algorithm)

The result of pairs.py is a .csv file with all pairs. It contains the follwoing fields:
1. year
2. first_letters
3. pair
4. man
5. woman
6. child
7. age
8. uuid
9. man_uuid
10. woman_uuid
11. child_uuid

year:
Year the event took place yyyy

first_letters:
First letter of last name man + first letter of last name woman

pair:
Type of pair (integer)
1: parents of newborn
2: groom and bride
3: parents of groom
4: parents of the bride
5: deceased and partner
6: parents of deceased

man:
Name of the man. Processed like above.

woman:
Name of the woman. Processed like above.

child:
Name of the child. Processed like above.
"" if no child is provided

age:
Either the age of the bride of groom, depending on the type of pair. 
age of bride if pair type is 1 or 3
age of groom if pair type is 2
-1 if age is unknown or pair is other type

uuid:
uuid of the certificate.

man_uuid:
uuid of the person reference of the man.

woman_uuid:
uuid of the person reference of the woman.

child_uuid:
uuid of the person reference of the child.
"" if no child is provided

Note that for pair type 5 (deceased and partner) the sex is unknown. The deceased will be treated as the man and their partner as the woman. This causes an issue in the linker. The order of the names affects the Levenshtein distance. The RecordLinker has a function to minimize this impact.

# RecordLinker: #

