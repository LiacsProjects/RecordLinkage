# Unique Historical Individual creation:
The Union Find algorith is used to calculate Unique Historical Individuals. This algorithm finds all uuids that are linked. These groups of linked uuids are given a unique integer. This is performed in "Unique Individuals/individuals.py"

# Result comparison:
Now that the results of RecordLinker and BurgerLinker are generated and formatted, the quality can be compared. 

Basic statistics are generated:
- Number of Unique Historical Individuals
- Number of unique person references that are linked
- Average number of linked person references per Unique Historical Individual

To generate more complicated statistics, details are added to the unique historical individuals. To each linked person reference "sex", "name", "role" are added. This makes it possible to validate the life courses. The role describes what type of person reference it is. For example a parent or groom.

Historgrams are created to capture the following detailed information:
- Histogram of births (number of births per Unique Historical Individual)
- Histogram of death (number of deaths per Unique Historical Individual)
- Histogram of group size (number of uuids per Unique Historical Individual)
- Completeness graph (number of "complete" life courses)
