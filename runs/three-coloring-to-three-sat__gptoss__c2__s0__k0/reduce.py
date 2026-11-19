"""Reduction from 3-Coloring to 3-SAT.

The source problem ``ThreeColoring`` expects an instance of the form::

    {"n": n, "edges": [[u, v], ...]}

where vertices are numbered ``0..n-1`` and each edge is an undirected pair.

The target problem ``ThreeSat`` expects an instance of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Each literal ``li`` is an integer ``+v`` (meaning variable ``v`` is true) or
``-v`` (meaning variable ``v`` is false).  Every clause must contain exactly
three *different* variables.

The reduction is classic: for each vertex ``i`` we create three Boolean
variables ``x_{i,0}``, ``x_{i,1}``, ``x_{i,2}`` indicating which colour the
vertex receives.  The SAT formula enforces:

1. **Exactly one colour per vertex** – at least one colour (a 3‑literal
   clause) and at most one colour (pairwise mutual exclusion).  The
   mutual‑exclusion constraints are originally 2‑literal clauses of the form
   ``(~x_{i,c1} ∨ ~x_{i,c2})``.  Because the target format only allows three
   literals, each such clause is replaced by two 3‑literal clauses using a
   fresh auxiliary variable ``y``:

       (~x ∨ ~y ∨  y)   ≡   (~x ∨ ~y)   (since one of ``y``/``-y`` must be true)

   Concretely we add ``(~x ∨ ~x' ∨  y)`` and ``(~x ∨ ~x' ∨ -y)``.  The two
   clauses together are satisfiable iff the original 2‑literal clause is
   satisfied, and they respect the three‑literal requirement.

2. **Adjacent vertices receive different colours** – for each edge ``(u,v)``
   and each colour ``c`` we add the clause ``(~x_{u,c} ∨ ~x_{v,c})`` using the
   same auxiliary‑variable trick.

All auxiliary variables are fresh and never appear elsewhere, guaranteeing
that each clause contains three distinct variables.

The construction runs in polynomial time and produces a formula that is
 satisfiable iff the original graph is 3‑colorable.
"""

from __future__ import annotations

from typing import Dict, List, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to a 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of ``[u, v]`` pairs).

    Returns
    -------
    dict
        A 3‑SAT instance in the format required by ``ThreeSat``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance.get("edges", [])

    # Assign a variable index to each (vertex, colour) pair.
    # var_id[i][c] = positive integer identifier for x_{i,c}
    var_id: List[List[int]] = [[0, 0, 0] for _ in range(n)]
    next_var: int = 1
    for i in range(n):
        for c in range(3):
            var_id[i][c] = next_var
            next_var += 1

    clauses: List[List[int]] = []

    # 1. Each vertex receives at least one colour.
    for i in range(n):
        clauses.append([var_id[i][0], var_id[i][1], var_id[i][2]])

    # Helper to encode a 2‑literal clause (a ∨ b) using an auxiliary variable.
    def encode_two_literal(a: int, b: int) -> None:
        """Encode (a ∨ b) with two 3‑literal clauses using a fresh aux variable.

        The auxiliary variable ``y`` is introduced such that the pair of
        clauses ``[a, b,  y]`` and ``[a, b, -y]`` is equivalent to ``(a ∨ b)``.
        """
        nonlocal next_var
        y = next_var
        next_var += 1
        clauses.append([a, b, y])
        clauses.append([a, b, -y])

    # 2. At most one colour per vertex (pairwise exclusion).
    for i in range(n):
        # colour pairs (0,1), (0,2), (1,2)
        pairs = [(0, 1), (0, 2), (1, 2)]
        for c1, c2 in pairs:
            a = -var_id[i][c1]
            b = -var_id[i][c2]
            encode_two_literal(a, b)

    # 3. Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in range(3):
            a = -var_id[u][c]
            b = -var_id[v][c]
            encode_two_literal(a, b)

    num_vars = next_var - 1
    return {"num_vars": num_vars, "clauses": clauses}

