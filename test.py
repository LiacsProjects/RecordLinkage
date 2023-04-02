import unidecode

WHITELIST = set("abcdefghijklmnopqrstuvwxyz")

AGE_MARRIED_RANGE = {"min": 15,
                     "max": 80}

AGE_MOTHER_RANGE = {"min": 15,
                    "max": 50}

AGE_DEATH_RANGE = {"min": 0,
                    "max": 100}


def clean(chars):
    if isinstance(chars, str):
        chars = str(chars).lower()
        chars = unidecode.unidecode(chars)
        chars = "".join(filter(WHITELIST.__contains__, chars))
        chars = chars.replace("ch", "g").replace("c", "k").replace("z", "s").replace("ph", "f").replace("ij", "y")
        return chars


def get_period(mode, age=0):
        start = None
        end = None
        
        if mode == 1:
            start = AGE_MOTHER_RANGE["min"]
            end = AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"] - AGE_MARRIED_RANGE["min"]
            if age > 14:
                end = AGE_MOTHER_RANGE["max"] - age + AGE_MARRIED_RANGE["max"]
        
        elif mode == 2:
            start = max(0, AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]
            if age != 0:
                end = AGE_MOTHER_RANGE["max"] - age
        
        elif mode == 3:
            start = AGE_MOTHER_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + AGE_MARRIED_RANGE["min"])
            if age != 0:
                start = AGE_MOTHER_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + age)
                end = AGE_MOTHER_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + age)

        elif mode == 4:
            start = AGE_MOTHER_RANGE["min"] - AGE_MOTHER_RANGE["max"]
            end = AGE_MOTHER_RANGE["max"] - AGE_MOTHER_RANGE["min"]
        
        elif mode == 5:
            start = AGE_MOTHER_RANGE["min"] + AGE_DEATH_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + AGE_MARRIED_RANGE["max"])
            end = AGE_MOTHER_RANGE["max"] + AGE_DEATH_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + AGE_MARRIED_RANGE["min"])
            if age != 0:
                start = AGE_MOTHER_RANGE["min"] + AGE_DEATH_RANGE["min"] - (AGE_MOTHER_RANGE["max"] + age)
                end = AGE_MOTHER_RANGE["max"] + AGE_DEATH_RANGE["max"] - (AGE_MOTHER_RANGE["min"] + age)

        
        return {"start": start, "end": end}
    

# print(get_period(1))
# print(get_period(2))
# print(get_period(3))
# print(get_period(4))
# print(get_period(5))




# print(get_period(1, 25))
# print(get_period(2, 25))
# print(get_period(3, 25))
# print(get_period(4, 25))
# print(get_period(5, 25))



print(10_000_000)



# print(clean("dënial'd wlkjdg dhgsd374twq"))