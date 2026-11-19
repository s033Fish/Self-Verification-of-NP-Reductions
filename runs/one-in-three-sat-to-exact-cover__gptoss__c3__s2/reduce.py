"""Reduction from 1-in-3-SAT to Exact Cover.

The source problem is :class:`OneInThreeSat` defined in ``problems.py``.
The target problem is :class:`ExactCover` defined in the same file.

Reduction idea
==============
For a 1‑in‑3‑SAT instance we have ``m`` variables and a list of clauses,
each clause being a triple of *positive* variable indices.  We need to pick a
truth assignment such that **exactly one** variable in each clause is true.

Consider the universe to be the set of clause indices ``0 .. C‑1`` where ``C``
is the number of clauses.  For every variable ``v`` (1‑based) create a set
``S_v`` containing the indices of the clauses in which ``v`` occurs.  Selecting
some collection of these variable‑sets covers each clause exactly once **iff**
the chosen variables constitute a truth assignment where each clause has
exactly one true variable.  This is precisely the definition of Exact Cover.

Variables that never appear generate the empty set – they are irrelevant for
Exact Cover and can be omitted.

The construction is clearly polynomial: we scan the clause list once and
populate ``m`` lists.
"""

from __future__ import annotations

from typing import Dict, List

from problems import OneInThreeSat, ExactCover


def reduce(instance: Dict) -> Dict:
    """Reduce a 1‑in‑3‑SAT instance to an Exact Cover instance.

    Parameters
    ----------
    instance: dict
        A valid 1‑in‑3‑SAT instance as described in ``problems.py``.

    Returns
    -------
    dict
        An Exact Cover instance.  ``universe_size`` equals the number of
        clauses and ``sets`` contains, for each variable that appears in at
        least one clause, the list of clause indices where it appears.
    """
    # Validate source instance (will raise if malformed).
    OneInThreeSat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_vars: int = instance["num_vars"]

    # Build a list for each variable (1‑based indexing). Initialise empty lists.
    var_to_clauses: List[List[int]] = [[] for _ in range(num_vars + 1)]

    for idx, clause in enumerate(clauses):
        # clause is a list of three distinct positive variable numbers.
        for var in clause:
            var_to_clauses[var].append(idx)

    # Convert to the list of sets required by ExactCover. Omit empty sets – they
    # are allowed but never useful.
    sets: List[List[int]] = [lst for lst in var_to_clauses[1:] if lst]

    exact_cover_instance = {
        "universe_size": len(clauses),
        "sets": sets,
    }

    # Validate the produced target instance for safety.
    ExactCover.validate(exact_cover_instance)
    return exact_cover_instance

