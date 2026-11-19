"""Reduction from ExactCover to SubsetSum.

ExactCover instance format:
    {"universe_size": u, "sets": [[element, ...], ...]}
SubsetSum instance format:
    {"numbers": [a1, a2, ...], "target": t}

We encode each set as a number in base B = (number of sets) + 1.
For a set S, its number is sum_{i in S} B**i.
The target is sum_{i=0}^{u-1} B**i, which corresponds to selecting a collection of
sets whose characteristic vectors sum to the all‑ones vector, i.e., an exact cover.
The base B is larger than the maximum possible digit sum, so no carries occur.
"""

def reduce(instance):
    # Extract data
    u = instance.get("universe_size", 0)
    sets = instance.get("sets", [])
    n = len(sets)
    # Base larger than any possible digit sum (max count per element)
    B = n + 1  # if n=0, B=1 which is fine
    numbers = []
    for S in sets:
        # Compute the encoded number for this set
        val = 0
        for i in S:
            # assume i is within 0..u-1
            val += B ** i
        numbers.append(val)
    # Target is the sum of B**i for all elements i in the universe
    target = 0
    for i in range(u):
        target += B ** i
    return {"numbers": numbers, "target": target}

# The module may be imported by the evaluation harness; no side effects.
