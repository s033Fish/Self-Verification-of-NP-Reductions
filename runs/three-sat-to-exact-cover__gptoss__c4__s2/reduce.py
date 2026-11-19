"""Reduction from 3‑SAT to Exact Cover.

Standard Karp reduction:

* Universe elements:
    - One element for each clause (indices 0..k-1).
    - Two elements for each variable x_i: p_i (positive literal) and n_i (negative literal).
      Indices: p_i = k + 2*(i-1), n_i = p_i + 1.
* Sets:
    1. For each clause C_j and each literal ℓ in C_j, add the set {j, lit_index(ℓ)}.
    2. For each variable x_i, add the set {p_i, n_i}.

An exact cover exists iff the 3‑SAT formula is satisfiable.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, ExactCover


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Exact Cover instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the :class:`ThreeSat` format.

    Returns
    -------
    dict
        An Exact Cover instance equivalent to the input formula.
    """
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    k = len(clauses)

    universe_size = k + 2 * m
    sets: List[List[int]] = []

    def lit_index(lit: int) -> int:
        var = abs(lit)
        base = k + 2 * (var - 1)
        return base if lit > 0 else base + 1

    # Clause‑literal sets
    for j, clause in enumerate(clauses):
        for lit in clause:
            sets.append([j, lit_index(lit)])

    # Variable pair sets
    for i in range(1, m + 1):
        pos = k + 2 * (i - 1)
        neg = pos + 1
        sets.append([pos, neg])

    return {"universe_size": universe_size, "sets": sets}

