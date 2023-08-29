# BurgerLinker: #
https://github.com/CLARIAH/burgerLinker/
The details on inner workings and use case can be found in the repository mentioned above.

# Data Preprocessing: #
The input files supplied by ELO need to be processed in order to apply BurgerLinker. BurgerLinker does not support divorce certificates. The files to process:
- Geboorte.csv
- Huwelijk.csv
- Overlijden.csv

BurgerLinker uses a RDF data structure. A tool is provided to convert .csv files to .nq files ("BurgerLinker/toRDF.py"). First, the input data needs to be formatted correctly for this tool to work.An example of the format can be found here:
https://github.com/CLARIAH/burgerLinker/tree/main/assets/csv-to-rdf/zeeland-dataset

*In essence, the certificates are described in one .csv file and the persons mentioned on them in another

1. Format the input .csv files to the correct format. The following Python scripts are used for this:
- "BurgerLinker/format Birth.py"
- "BurgerLinker/format Marriage.py"
- "BurgerLinker/format Death.py"

These scripts produce 6 .csv files; a registration file and a person file for each certificate type. The script are located in "BurgerLinker/input"

2. "BurgerLinker/toRDF.py" is run to create 6 .nq files. 

3. The 6 .nq files are combined into one .nq file. The following command combines two files into one:
"cat registrations.nq persons.nq > myCivilRegistries.nq"

4. The one .nq file is used as input for BurgerLinker. The ConvertToHDT function is called. A HDT file and index file is created. This data structure is used to create the certificate links.

# Result processing: #
BurgerLinker returns .csv files containing linked certificate pairs. To produce unique historical individuals, person links need to be generated. This is done in "BurgerLinker/processing.py".

This script looks at the linked certificates to reverse engineer what persons where compared. The compared person references need to be linked. Some linking modes are straight forward, because the same roles are always linked. Other modes are more complicated, because the Levenshtein distance needs to be calculated again to determine what persons are the same. For example, when parents of married couples are linked, it is not clear if the parents of the bride or groom were linked. The names with the smallest distance are saved.

The .csv file with person references contains, for each person link, the linked uuids, the linking mode and the sex of the person.
