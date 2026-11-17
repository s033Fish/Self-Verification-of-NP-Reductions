"""Broken: the budget is off by one (n - k + 1 instead of n - k)."""


def reduce(instance):
    n = instance["n"]
    return {"n": n, "edges": instance["edges"], "k": n - instance["k"] + 1}