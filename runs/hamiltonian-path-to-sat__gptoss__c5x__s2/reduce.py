"""Reduction from Hamiltonian Path to SAT.

The source problem is :class:`HamiltonianPath` defined in ``problems.py``.
The target problem is :class:`Sat` (CNF satisfiability).

The reduction follows the classic textbook encoding using a variable
``X_{i,v}`` that is true iff vertex ``v`` occupies position ``i`` in the
Hamiltonian path.  Variables are numbered from 1 to ``n*n`` where ``n`` is
the number of vertices.  The generated CNF enforces:

1. **Each position contains exactly one vertex** – a clause with all
   ``X_{i,v}`` (at least one) and pairwise mutual‑exclusion clauses
   ``¬X_{i,v} ∨ ¬X_{i,w}`` for ``v != w``.
2. **Each vertex appears exactly once** – analogous clauses over the
   positions.
3. **Consecutive vertices must be adjacent** – for every non‑edge
   ``{v,w}`` and every position ``i`` we add ``¬X_{i,v} ∨ ¬X_{i+1,w}``.

Edge cases are handled explicitly so that the reduction runs in constant
time for ``n = 0`` or ``n = 1``:

* ``n = 0`` – the Hamiltonian‑Path instance is a definite *no*.  We return
  a SAT instance containing a single empty clause ``[]`` which is always
  unsatisfiable.
* ``n = 1`` – the instance is a definite *yes*.  An empty CNF (no clauses)
  is always satisfiable, so we return ``{"num_vars": 0, "clauses": []}``.

The function validates the input using the class method provided in
``problems.py`` and returns a dictionary that conforms to the SAT instance
format.
"""

from __future__ import annotations

from itertools import combinations
from typing import List, Dict, Any, Set

from problems import HamiltonianPath, Sat


def _var_index(i: int, v: int, n: int) -> int:
    """Map position ``i`` and vertex ``v`` to a SAT variable number.

    Variables are numbered from 1 to ``n*n`` in row‑major order:
    ``X_{0,0}`` → 1, ``X_{0,1}`` → 2, …, ``X_{n-1,n-1}`` → ``n*n``.
    """
    return i * n + v + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Hamiltonian‑Path instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` as described in the
        docstring of :class:`HamiltonianPath`.

    Returns
    -------
    dict
        A SAT instance dictionary with keys ``"num_vars"`` and ``"clauses"``.
    """
    # Validate the source instance – will raise InvalidInstance on error.
    HamiltonianPath.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Edge‑case handling.
    if n == 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if n == 1:
        # Trivially satisfiable (empty CNF).
        return {"num_vars": 0, "clauses": []}

    # Build a set of existing undirected edges for O(1) lookup.
    edge_set: Set[frozenset[int]] = {frozenset(e) for e in edges}

    num_vars = n * n
    clauses: List[List[int]] = []

    # 1. Each position i contains at least one vertex.
    for i in range(n):
        clause = [_var_index(i, v, n) for v in range(n)]
        clauses.append(clause)

    # 1b. Each position contains at most one vertex (pairwise exclusion).
    for i in range(n):
        for v, w in combinations(range(n), 2):
            clauses.append([-_var_index(i, v, n), -_var_index(i, w, n)])

    # 2. Each vertex appears in at least one position.
    for v in range(n):
        clause = [_var_index(i, v, n) for i in range(n)]
        clauses.append(clause)

    # 2b. Each vertex appears at most once.
    for v in range(n):
        for i, j in combinations(range(n), 2):
            clauses.append([-_var_index(i, v, n), -_var_index(j, v, n)])

    # 3. Adjacent‑position edge constraints.
    # For every non‑edge {v,w} and every position i, forbid v at i and w at i+1.
    for i in range(n - 1):
        for v in range(n):
            for w in range(n):
                if v == w:
                    continue
                if frozenset((v, w)) not in edge_set:
                    clauses.append([
                        -_var_index(i, v, n),
                        -_var_index(i + 1, w, n),
                    ])

    # Return the SAT instance.
    return {"num_vars": num_vars, "clauses": clauses}

