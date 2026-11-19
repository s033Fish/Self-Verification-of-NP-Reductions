"""Reduction from Dominating Set to SAT.

The source problem instance is a dictionary with keys:
    - "n": number of vertices (0-indexed vertices 0..n-1)
    - "edges": list of undirected edges [u, v] with u != v
    - "k": size bound for the dominating set (we need a set of size ≤ k)

The target problem is SAT in CNF.  An instance is a dictionary with keys:
    - "num_vars": total number of Boolean variables (numbered 1..m)
    - "clauses": list of clauses, each clause is a list of literals.
      A literal is a signed integer: ``+v`` means variable *v* is true,
      ``-v`` means variable *v* is false.

The reduction creates a Boolean variable ``x_i`` (1‑based) for each vertex
``i`` of the graph indicating whether the vertex belongs to the dominating
set.  Two groups of clauses are added:

1. **Domination clauses** – for every vertex ``v`` we add a clause that
   requires ``v`` itself or one of its neighbours to be selected:
   ``(x_v ∨ x_u1 ∨ x_u2 ∨ …)``.

2. **Cardinality constraint** – at most ``k`` of the ``x_i`` may be true.
   This is encoded using the classic *sequential counter* (Sinz 2005),
   which introduces auxiliary variables ``s_{i,j}`` meaning “among the
   first *i* vertices at least *j* are selected”.  The encoding uses a
   linear number of auxiliary variables (``n·k``) and a linear number of
   clauses, therefore the reduction runs in polynomial time.

Edge‑case handling follows the specification of the source problem:

* ``k < 0`` – always a NO instance; we return a formula containing an empty
  clause (unsatisfiable).
* ``n == 0`` – always a YES instance; we return an empty formula (trivially
  satisfiable).
* ``k >= n`` – always YES; again an empty formula suffices.

The function ``reduce`` implements the above logic and returns a SAT
instance that is satisfiable iff the original Dominating‑Set instance has a
dominating set of size at most ``k``.
"""

from __future__ import annotations
from typing import Dict, List, Any, Tuple


def _sequential_counter_clauses(n: int, k: int) -> Tuple[List[List[int]], int]:
    """Return clauses encoding ``≤ k`` true variables among ``x_1..x_n``.

    The function returns a pair ``(clauses, total_vars)`` where ``total_vars``
    is the number of variables after introducing the auxiliary ones.
    The encoding follows Sinz, *Towards an Efficient CNF Encoding of Boolean
    Cardinality Constraints*, 2005.
    """
    clauses: List[List[int]] = []
    aux: dict[Tuple[int, int], int] = {}
    var_counter = n  # start after the original x_i variables

    def get_aux(i: int, j: int) -> int:
        nonlocal var_counter
        key = (i, j)
        if key not in aux:
            var_counter += 1
            aux[key] = var_counter
        return aux[key]

    if k == 0:
        for i in range(1, n + 1):
            clauses.append([-i])
        return clauses, var_counter

    # Base case: s_{1,1} ↔ x_1
    s11 = get_aux(1, 1)
    clauses.append([-1, s11])
    clauses.append([1, -s11])

    # j = 1 for i >= 2
    for i in range(2, n + 1):
        si1 = get_aux(i, 1)
        clauses.append([-i, si1])
        s_prev1 = get_aux(i - 1, 1)
        clauses.append([-s_prev1, si1])

    # General case j >= 2
    for i in range(2, n + 1):
        for j in range(2, k + 1):
            sij = get_aux(i, j)
            s_prev_j = get_aux(i - 1, j)
            s_prev_jm1 = get_aux(i - 1, j - 1)
            clauses.append([-i, -s_prev_jm1, sij])
            clauses.append([-s_prev_j, sij])

    # Final constraints to forbid exceeding k selections.
    for i in range(1, n):
        s_i_k = get_aux(i, k)
        clauses.append([-(i + 1), -s_i_k])

    return clauses, var_counter


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Dominating‑Set instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"``.

    Returns
    -------
    dict
        SAT instance in the format required by ``problems.py``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge‑case handling.
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}
    if n == 0:
        return {"num_vars": 0, "clauses": []}
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # Build adjacency list.
    neigh: List[set[int]] = [set() for _ in range(n)]
    for u, v in edges:
        neigh[u].add(v)
        neigh[v].add(u)

    clauses: List[List[int]] = []

    # Domination clauses.
    for v in range(n):
        lits = [v + 1]
        for nb in neigh[v]:
            lits.append(nb + 1)
        clauses.append(lits)

    # Cardinality constraints.
    card_clauses, total_vars = _sequential_counter_clauses(n, k)
    clauses.extend(card_clauses)

    return {"num_vars": total_vars, "clauses": clauses}

