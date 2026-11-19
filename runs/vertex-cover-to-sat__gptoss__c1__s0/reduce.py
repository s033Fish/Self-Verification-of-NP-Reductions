"""Reduction from Vertex Cover to SAT.

The source problem is defined in ``problems.py`` as ``VertexCover`` with
instances of the form ``{"n": n, "edges": [[u, v], ...], "k": k}``.

The target problem is ``Sat`` with instances ``{"num_vars": m,
"clauses": [[literal, ...], ...]}``.  Literals are encoded as signed
integers: ``+v`` (positive) means variable ``v`` is true, ``-v`` means it
is false.  Variables are numbered from ``1`` to ``m``.

The reduction follows the classic textbook construction:

* For each vertex ``i`` (0‑based) and each possible position ``j`` in a
  cover of size ``k`` we create a Boolean variable ``x_{i,j}`` that is
  true iff vertex ``i`` occupies position ``j`` in the cover.
* The constraints are encoded as CNF clauses:
    1. **Every position is filled** – for each ``j`` we add a clause that
       at least one vertex occupies that position.
    2. **No position holds two vertices** – for each ``j`` and each pair
       of distinct vertices ``i < i'`` we add a clause ``¬x_{i,j} ∨ ¬x_{i',j}``.
    3. **A vertex cannot occupy two positions** – for each vertex ``i``
       and each pair of distinct positions ``j < j'`` we add a clause
       ``¬x_{i,j} ∨ ¬x_{i,j'}``.
    4. **Edge coverage** – for each edge ``(u, v)`` we add a clause that
       at least one of its endpoints appears somewhere in the cover:
       ``x_{u,1} ∨ … ∨ x_{u,k} ∨ x_{v,1} ∨ … ∨ x_{v,k}``.

The reduction handles the trivial edge‑cases directly:

* ``k < 0`` – the vertex‑cover instance is a definite NO.  We output a SAT
  instance containing a single empty clause ``[]`` which is unsatisfiable.
* ``k >= n`` or the graph has no edges – the instance is a definite YES.
  We output an empty CNF (no clauses), which is always satisfiable.

The function runs in time polynomial in ``n``, ``|E|`` and ``k``.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a Vertex Cover instance to a SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"``, ``"edges"`` and ``"k"`` as
        described in the problem statement.

    Returns
    -------
    dict
        A SAT instance in the required format.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases -----------------------------------------------------------
    # k < 0 -> always NO, produce unsatisfiable formula (empty clause).
    if k < 0:
        return {"num_vars": 0, "clauses": [[]]}

    # If k >= n or there are no edges, the answer is always YES.
    if k >= n or not edges:
        return {"num_vars": 0, "clauses": []}

    # General case ----------------------------------------------------------
    # Number of variables = n * k.  Variable id for (i, j) where i in [0,n)
    # and j in [0,k) is i * k + j + 1 (SAT variables start at 1).
    num_vars = n * k
    clauses: List[List[int]] = []

    # 1. Every position j (0..k-1) must be occupied by at least one vertex.
    for j in range(k):
        clause = [i * k + j + 1 for i in range(n)]
        clauses.append(clause)

    # 2. No position j can contain two different vertices.
    for j in range(k):
        for i in range(n):
            vi = i * k + j + 1
            for i2 in range(i + 1, n):
                v2 = i2 * k + j + 1
                clauses.append([-vi, -v2])

    # 3. No vertex i can appear in two different positions.
    for i in range(n):
        for j in range(k):
            vj = i * k + j + 1
            for j2 in range(j + 1, k):
                vj2 = i * k + j2 + 1
                clauses.append([-vj, -vj2])

    # 4. Edge coverage clauses.
    for (u, v) in edges:
        clause: List[int] = []
        for j in range(k):
            clause.append(u * k + j + 1)
            clause.append(v * k + j + 1)
        clauses.append(clause)

    return {"num_vars": num_vars, "clauses": clauses}

