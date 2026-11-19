import copy

def reduce(instance):
    """Reduce Subset Sum instance to Partition instance.
    Input instance format: {"numbers": [a1, a2, ...], "target": t}
    Output instance format: {"numbers": [b1, b2, ...]}
    """
    numbers = instance.get("numbers", [])
    t = instance.get("target", 0)
    # Edge cases directly map to trivial partition instances.
    if t == 0:
        # Subset sum always yes via empty subset. Return empty list which is yes for partition.
        return {"numbers": []}
    if t < 0:
        # Source is always no. Return a partition instance that is obviously no (odd total).
        return {"numbers": [1, 2]}  # sum=3 odd => no
    total = sum(numbers)
    if t > total:
        # Cannot achieve target, source no. Return a no-instance for partition.
        return {"numbers": [1, 2]}
    # At this point 0 < t <= total.
    # Ensure target does not exceed half of total by possibly using complement.
    if t > total / 2:
        t = total - t
    # Now t <= total/2, define extra element X = total - 2*t (non‑negative).
    X = total - 2 * t
    # Construct new list.
    new_numbers = copy.deepcopy(numbers)
    new_numbers.append(X)
    return {"numbers": new_numbers}

# The module may be imported; no top‑level execution needed.
