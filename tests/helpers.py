import random


def _rand_list(count, max_):
    return [random.randint(1, max_) for _ in range(count)]
