"""Broken: forgets the t < 0 / t > S guard, so 2S - t can go negative."""


def reduce(instance):
    numbers, target = instance["numbers"], instance["target"]
    total = sum(numbers)
    return {"numbers": numbers + [2 * total - target, total + target]}