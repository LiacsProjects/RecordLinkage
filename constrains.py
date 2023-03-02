AGE_MARRIED_RANGE = {"min": 15,
                     "max": 70}

AGE_MOTHER_RANGE = {"min": 15,
                    "max": 45}

year = 1900
age_bride = 20

age_mother_bride = {"min": age_bride + AGE_MOTHER_RANGE["min"], 
                    "max": age_bride + AGE_MOTHER_RANGE["max"]}



def get_period(link_type, age:int=None):
    start = None
    end = None
    if link_type == "hp-ho":
        start = AGE_MOTHER_RANGE["min"]
        end = AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"] - AGE_MOTHER_RANGE["min"]
        if age != None:
            start = AGE_MOTHER_RANGE["min"]
            end = AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"] - age 
    
    elif link_type == "hp-b":
        start = max(0, AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"])
        end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]
        if age != None:
            start = max(0, AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - age
    
    elif link_type == "ho-b":
        start = AGE_MOTHER_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"])
        end = AGE_MOTHER_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + AGE_MOTHER_RANGE["min"])
    
    elif link_type == "b-b":
        start = AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"]
        end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]
    
    return {"start": start, "end": end}

    
print(get_period("hp-ho"))
print(get_period("hp-b"))
print(get_period("ho-b"))
print(get_period("b-b"))
print("---------------")
print(get_period("hp-ho", 25))
print(get_period("hp-b", 25))
print(get_period("ho-b", 25))
print(get_period("b-b", 25))






# print(age_mother_bride)

# print(AGE_MARRIED_RANGE)

# # timedifference = {"earliest": age_mother_bride["max"] - AGE_MARRIED["min"], 
# #                   "latest": age_mother_bride["max"] - AGE_MARRIED["min"]}

# # print(timedifference)
# print(age_mother_bride["max"] - AGE_MARRIED_RANGE["min"])
# print(age_mother_bride["max"] - AGE_MARRIED_RANGE["max"])
# print(age_mother_bride["min"] - AGE_MARRIED_RANGE["min"])
# print(age_mother_bride["min"] - AGE_MARRIED_RANGE["max"])


# 55 - 30


# difference = {max(0, age_bride - AGE_MOTHER_RANGE["min"]),
#               AGE_MOTHER_RANGE["max"] - age_bride}

# print(difference)

        








# age_mother_married = {"min": age_mother_bride, 
#                       "max": age_mother_bride}

# print(age_mother_bride)
