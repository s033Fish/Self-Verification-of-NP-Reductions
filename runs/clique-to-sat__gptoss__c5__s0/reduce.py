"""Reduction from Clique to SAT.

The source problem is :class:`Clique` (defined in ``problems.py``) and the
target problem is :class:`Sat`.  The reduction follows the classic polynomial‑
time transformation used in textbooks:

* For each vertex ``v`` (0‑based) and each possible position ``p`` in a
  clique of size ``k`` we introduce a Boolean variable ``X_{v,p}`` that is true
  exactly when vertex ``v`` occupies position ``p``.
* The constraints are encoded as CNF clauses:

  1. **Every position is occupied** – for each ``p`` a clause containing all
     ``X_{v,p}`` (positive literals).
  2. **At most one vertex per position** – for each ``p`` and each pair of
     distinct vertices ``v != w`` a clause ``¬X_{v,p} ∨ ¬X_{w,p}``.
  3. **A vertex appears in at most one position** – for each vertex ``v`` and
     each pair of distinct positions ``p != q`` a clause ``¬X_{v,p} ∨ ¬X_{v,q}``.
  4. **Non‑edges cannot both be selected** – for every unordered pair ``{v,w}``
     that is *not* an edge of the graph and for each pair of positions ``p, q``
     (including ``p == q``) a clause ``¬X_{v,p} ∨ ¬X_{w,q}``.

If the original instance is a trivial *yes* (``k <= 0`` or ``k == 1`` with
``n >= 1``) we output an empty CNF (no variables, no clauses) which is always
 satisfiable.  If ``k > n`` we output a formula containing a single empty clause
 – unsatisfiable regardless of the number of variables.

The function ``reduce`` validates the input using ``Clique.validate`` and then
returns a dictionary that conforms to the ``Sat`` instance format.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import Clique, Sat, InvalidInstance


def _var_index(v: int, p: int, k: int) -> int:
    """Map vertex ``v`` (0‑based) and position ``p`` (0‑based) to a SAT variable.

    Variables are numbered from 1 to ``n * k`` in row‑major order:
    ``index = v * k + p + 1``.
    """
    return v * k + p + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a Clique instance to an equivalent SAT instance.

    The returned instance satisfies the ``Sat`` format defined in
    ``problems.py``.  The reduction runs in time polynomial in ``n`` and ``k``.
    """
    Clique.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases -----------------------------------------------------------
    if k <= 0:
        return {"num_vars": 0, "clauses": []}
    if k == 1:
        if n >= 1:
            return {"num_vars": 0, "clauses": []}
    if k > n:
        return {"num_vars": 0, "clauses": [[]]}

    # Build adjacency set for quick lookup.
    adj: set[Tuple[int, int]] = set()
    for u, v in edges:
        if u > v:
            u, v = v, u
        adj.add((u, v))

    clauses: List[List[int]] = []
    num_vars = n * k

    # 1. Every position must be occupied by at least one vertex.
    for p in range(k):
        clauses.append([_var_index(v, p, k) for v in range(n)])

    # 2. At most one vertex per position.
    for p in range(k):
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_index(v, p, k), -_var_index(w, p, k)])

    # 3. A vertex appears in at most one position.
    for v in range(n):
        for p in range(k):
            for q in range(p + 1, k):
                clauses.append([-_var_index(v, p, k), -_var_index(v, q, k)])

    # 4. Non‑edges cannot both be selected (in any positions).
    for v in range(n):
        for w in range(v + 1, n):
            if (v, w) not in adj:  # not an edge
                for p in range(k):
                    for q in range(k):
                        clauses.append([-_var_index(v, p, k), -_var_index(w, q, k)])

    return {"num_vars": num_vars, "clauses": clauses}

