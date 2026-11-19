"""Reduction from 3‑SAT to Exact Cover.

This follows Karp's classic reduction using clause elements and literal‑occurrence
elements.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, ExactCover


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an Exact Cover instance.

    Parameters
    ----------
    instance: dict with keys "num_vars" and "clauses".

    Returns
    -------
    dict representing an Exact Cover instance equivalent to the SAT instance.
    """
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    n = len(clauses)

    # Universe consists of n clause elements (0..n-1) and 3*n occurrence elements.
    universe_size = n + 3 * n
    sets: List[List[int]] = []

    # Map each occurrence to its clause index and literal.
    # occurrence index = n + i*3 + k for clause i, literal position k.
    # Build lists of occurrence indices for each variable polarity.
    pos_occ: dict[int, List[int]] = {v: [] for v in range(1, m + 1)}
    neg_occ: dict[int, List[int]] = {v: [] for v in range(1, m + 1)}

    for i, clause in enumerate(clauses):
        for k, lit in enumerate(clause):
            occ_idx = n + i * 3 + k
            # Clause set covering clause element i and this occurrence
            sets.append([i, occ_idx])
            var = abs(lit)
            if lit > 0:
                pos_occ[var].append(occ_idx)
            else:
                neg_occ[var].append(occ_idx)

    # For each variable, add a set for the positive polarity and one for the negative.
    for v in range(1, m + 1):
        if pos_occ[v]:
            sets.append(pos_occ[v].copy())
        if neg_occ[v]:
            sets.append(neg_occ[v].copy())

    target = {"universe_size": universe_size, "sets": sets}
    ExactCover.validate(target)
    return target

