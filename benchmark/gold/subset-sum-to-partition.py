"""Gold reduction: Subset Sum -> Partition.

Let S be the sum of the numbers and t the target. Add two numbers, 2S - t and
S + t, so the new total is 4S and each side of a partition must sum to 2S.
The two new numbers sum to 3S > 2S, so they land on opposite sides; the side
holding 2S - t then needs exactly t from the original numbers.

Edge case: when t < 0 or t > S the answer is no, and the new numbers could be
negative, so return a fixed no-instance instead.
"""


def reduce(instance):
    numbers, target = instance["numbers"], instance["target"]
    total = sum(numbers)
    if target < 0 or target > total:
        return {"numbers": [1]}  # odd total: never partitionable
    return {"numbers": numbers + [2 * total - target, total + target]}