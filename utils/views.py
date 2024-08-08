from itertools import zip_longest


def zip_cycle(*iterables, empty_default=None):
    # cycles = [cycle(i) for i in iterables]
    for _ in zip_longest(*iterables):
        yield _
        # print(_)
        # yield tuple(next(i, empty_default) for i in cycles)


# for i in zip_cycle(range(2), range(5), ['a', 'b', 'c'], []):
#     print(i)
