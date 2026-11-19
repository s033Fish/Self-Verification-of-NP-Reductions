"""Gold reduction: Exact Cover -> Subset Sum.            [test, famous]

SOURCE  Exact Cover  {"universe_size": u, "sets": [[element, ...], ...]}
TARGET  Subset Sum   {"numbers": [...], "target": t}  yes iff a sub-list sums to t

Construction: write numbers in base B = (number of sets) + 1, one digit per
element. Set S becomes the number sum of B^e for e in S. The target has a 1
in every digit: sum of B^e for e = 0..u-1.

"""


def reduce(instance):
    sets = instance["sets"]
    base = len(sets) + 1
    numbers = [sum(base ** e for e in s) for s in sets]
    target = sum(base ** e for e in range(instance["universe_size"]))
    return {"numbers": numbers, "target": target}