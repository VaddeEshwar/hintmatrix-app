# 2 => addition, 3=> subtraction, 0 => no operation.
ADDITION = 2
SUBTRACTION = 3

ARITHMETIC = (
    (ADDITION, "add"),
    (SUBTRACTION, "sub"),
)
ARITHMETIC_DICT = dict(ARITHMETIC)

ARITHMETIC_BY_VALUE = {value: key for key, value in ARITHMETIC}

# 11 => one to one, 112=> one to many
ONETOONE = 11
ONETOTWO = 121
ONETOTHREE = 131
ONETOFOUR = 141

RELATIONSHIP = (
    (ONETOONE, "1 TO 1"),
    (ONETOTWO, "1 TO 2"),
    (ONETOTHREE, "1 TO 3"),
    (ONETOFOUR, "1 TO 4"),
)
RELATIONSHIP_DICT = dict(RELATIONSHIP)

RELATIONSHIP_BY_VALUE = {value: key for key, value in RELATIONSHIP}
