import random
import string

__author__ = "Naresh"


def generate_random_key(txt, integer):
    key = str(txt) + str(integer)
    key = "".join(random.SystemRandom().choice(key) for _ in range(len(key)))
    return key


def id_generator(size=16, special=False, chars=string.ascii_uppercase + string.digits):
    if special:
        chars += string.punctuation
    return "".join(random.choice(chars) for _ in range(size))


def code_generator(size=8):
    return id_generator(size=size)
