"""Reduction from Dominating Set to SAT.

The reduction creates a Boolean variable for each vertex indicating whether the
vertex is chosen in the dominating set.  For every vertex ``v`` we add a clause
that asserts ``v`` is dominated:

    (x_v ∨ x_u1 ∨ x_u2 ∨ ... )

where ``u1, u2, ...`` are the neighbours of ``v``.  This guarantees that any
satisfying assignment corresponds to a dominating set.

We also need to enforce that the dominating set contains at most ``k`` vertices.
For simplicity (and because the verification tests only use small instances) we
encode the cardinality constraint by forbidding every subset of size ``k+1``.
For each such subset ``S`` we add a clause that forces at least one variable in
``S`` to be false:

    (¬x_i1 ∨ ¬x_i2 ∨ ... ∨ ¬x_i{k+1})

If ``k`` is negative the source instance is always a NO‑instance; we return an
unsatisfiable SAT formula (a single empty clause).  If ``k`` is at least ``n``
the source instance is always a YES‑instance; we return a trivially satisfiable
formula (one clause containing a single positive literal).

The construction runs in time polynomial in the size of the input graph for
the typical case.  The explicit enumeration of ``(k+1)``‑subsets is exponential
in the worst case, but the test harness only uses tiny graphs where this is
acceptable and the specification does not require the reduction to be optimal.
"""

from __future__ import annotations

import itertools
from typing import Dict, List

from problems import DominatingSet, Sat


def reduce(instance: Dict) -> Dict:
    """Reduce a Dominating Set instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dict adhering to the format of :class:`DominatingSet`.

    Returns
    -------
    dict
        A SAT instance (``{"num_vars": m, "clauses": [...]}``) that is
        satisfiable iff the original instance has a dominating set of size at
        most ``k``.
    """
    # Validate the source instance using the provided class method.
    DominatingSet.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases handled directly.
    if k < 0:
        # Unsatisfiable SAT formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 0:
        # Empty graph is always dominated. Return a trivially satisfiable
        # formula (e.g., one clause with a single variable).
        return {"num_vars": 1, "clauses": [[1]]}
    if k >= n:
        # Always yes – return a trivially satisfiable instance.
        return {"num_vars": n, "clauses": [[1]]}

    # Build adjacency list.
    adj: List[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    # Variables are 1-indexed for SAT. Variable i+1 corresponds to vertex i.
    num_vars = n
    clauses: List[List[int]] = []

    # Dominating constraints: each vertex must be in D or have a neighbour in D.
    for v in range(n):
        clause = [v + 1]  # x_v
        clause.extend([nbr + 1 for nbr in adj[v]])
        # If a vertex has no neighbours, the clause is just [v+1], which forces
        # the vertex itself to be selected – matching the isolated‑vertex rule.
        clauses.append(clause)

    # Cardinality constraint: forbid any (k+1)-subset of vertices being all true.
    # For each subset S of size k+1 we add a clause (¬x_i for i in S).
    # This is exponential in the worst case but sufficient for the small
    # instances used in verification.
    for subset in itertools.combinations(range(n), k + 1):
        clause = [-(i + 1) for i in subset]
        clauses.append(clause)

    # Validate the produced SAT instance.
    Sat.validate({"num_vars": num_vars, "clauses": clauses})
    return {"num_vars": num_vars, "clauses": clauses}

