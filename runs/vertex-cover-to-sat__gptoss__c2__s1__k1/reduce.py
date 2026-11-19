"""Reduction from Vertex Cover to SAT.

The source problem is defined in ``problems.py`` as ``VertexCover`` with the
instance format::

    {"n": n, "edges": [[u, v], ...], "k": k}

The target problem is SAT (CNF satisfiability) with the instance format::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

The reduction follows the classic polynomial‑time transformation that uses a
binary matrix of size *n × k*.

*Variables* ``x_{i,p}`` (1 ≤ p ≤ k, 0 ≤ i < n) denote that vertex ``i`` occupies
the ``p``‑th position in a vertex cover of size at most ``k``.  The SAT formula
contains three groups of clauses:

1. **Cover size** – each position ``p`` must be occupied by at least one vertex.
2. **Uniqueness** – a vertex cannot appear in two different positions.
3. **Edge covering** – for every edge ``(u, v)`` at least one of its endpoints
   must appear in the cover (i.e. in some position).

The construction is polynomial in ``n``, ``|E|`` and ``k`` (``O(n·k + |E|·k)``
variables/clauses).  Edge cases are handled explicitly:

* ``k < 0`` – the answer is always *NO*.  We return a SAT instance that is
  unsatisfiable (a single empty clause).
* ``k >= n`` – the answer is always *YES*.  An empty CNF (no clauses) is
  trivially satisfiable, so we return ``num_vars = 0`` and no clauses.

The function ``reduce`` implements this transformation and runs in polynomial
time.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _var_index(i: int, p: int, k: int) -> int:
    """Map vertex ``i`` and position ``p`` (1‑based) to a SAT variable number.

    Variables are numbered from 1 to n*k inclusive.
    """
    # ``i`` is 0‑based, ``p`` is 1‑based.
    return i * k + p


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as described
        in the problem statement.

    Returns
    -------
    dict
        A SAT instance in the format required by ``problems.py``.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge case: k < 0 → always NO.  Return an unsatisfiable formula.
    if k < 0:
        # One variable is enough; an empty clause makes the formula unsat.
        return {"num_vars": 1, "clauses": [[]]}

    # Edge case: k >= n → always YES.  Empty CNF is satisfiable.
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # General case.
    num_vars = n * k
    clauses: List[List[int]] = []

    # 1. Each position p must be occupied by at least one vertex.
    for p in range(1, k + 1):
        clause = [_var_index(i, p, k) for i in range(n)]
        clauses.append(clause)

    # 2. A vertex cannot occupy two different positions.
    for i in range(n):
        for p in range(1, k):
            for q in range(p + 1, k + 1):
                clauses.append([-_var_index(i, p, k), -_var_index(i, q, k)])

    # 3. Every edge must be covered by at least one endpoint.
    for u, v in edges:
        clause = []
        for p in range(1, k + 1):
            clause.append(_var_index(u, p, k))
            clause.append(_var_index(v, p, k))
        clauses.append(clause)

    return {"num_vars": num_vars, "clauses": clauses}

