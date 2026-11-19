"""Reduction from 3-Coloring to 3-SAT.

The source problem (ThreeColoring) expects an instance of the form
```
{"n": n, "edges": [[u, v], ...]}
```
where vertices are numbered 0..n-1 and each edge is an unordered pair.

The target problem (ThreeSat) expects an instance of the form
```
{"num_vars": m, "clauses": [[l1, l2, l3], ...]}
```
where each clause contains exactly three *distinct* literals on distinct
variables.  A literal is a positive integer for the variable being true
or a negative integer for the variable being false.

The classic polynomial‑time reduction introduces three Boolean variables
for each vertex – one for each colour – and then adds constraints that
* each vertex receives at least one colour (a 3‑literal clause),
* no vertex receives two colours simultaneously (pairwise "not‑both"
  constraints), and
* adjacent vertices never share the same colour.

The pairwise constraints are naturally 2‑CNF clauses.  To satisfy the
requirement of exactly three literals per clause we replace a clause
``(a ∨ b)`` with the pair of 3‑clauses ``(a ∨ b ∨ y)`` and
``(a ∨ b ∨ ¬y)`` where ``y`` is a fresh auxiliary variable.  This
transformation preserves satisfiability because the auxiliary variable
can be set arbitrarily.

The implementation below follows this plan.  It runs in time polynomial
in the size of the input graph and produces a correctly formatted
ThreeSat instance.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to a 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and
        ``"edges"`` (list of ``[u, v]`` pairs).

    Returns
    -------
    dict
        A ThreeSat instance with keys ``"num_vars"`` and ``"clauses"``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Helper to map (vertex, colour) -> variable index (1‑based as required).
    # Colours are 0,1,2.
    def var(vertex: int, colour: int) -> int:
        return vertex * 3 + colour + 1  # +1 to make it 1‑based

    clauses: List[List[int]] = []
    next_aux: int = n * 3 + 1  # first auxiliary variable index

    # 1. Each vertex gets at least one colour: (R ∨ G ∨ B)
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # Function to replace a 2‑literal clause (l1 ∨ l2) with two 3‑literal
    # clauses using a fresh auxiliary variable.
    def add_two_literal_clause(lit1: int, lit2: int) -> None:
        nonlocal next_aux
        aux = next_aux
        next_aux += 1
        # (lit1 ∨ lit2 ∨ aux) and (lit1 ∨ lit2 ∨ ¬aux)
        clauses.append([lit1, lit2, aux])
        clauses.append([lit1, lit2, -aux])

    # 2. No vertex receives two colours simultaneously.
    for v in range(n):
        # pairs of colours: (0,1), (0,2), (1,2)
        colour_pairs = [(0, 1), (0, 2), (1, 2)]
        for c1, c2 in colour_pairs:
            # ¬R_v ∨ ¬G_v etc.
            add_two_literal_clause(-var(v, c1), -var(v, c2))

    # 3. Adjacent vertices cannot share the same colour.
    for u, v in edges:
        for c in range(3):
            add_two_literal_clause(-var(u, c), -var(v, c))

    num_vars = next_aux - 1  # because next_aux is one past the last used

    return {"num_vars": num_vars, "clauses": clauses}

