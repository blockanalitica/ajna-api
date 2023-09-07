import random


def generate_ethereum_address():
    return "0x{}".format("".join(random.choices("0123456789abcdef", k=40)))


def generate_transaction_hash():
    return "0x{}".format("".join(random.choices("0123456789abcdef", k=40)))
