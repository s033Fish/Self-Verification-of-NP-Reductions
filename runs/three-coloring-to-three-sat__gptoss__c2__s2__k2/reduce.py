"""Reduction from 3‑Coloring to 3‑SAT.

The source problem (ThreeColoring) expects an instance of the form
```
{"n": <number of vertices>, "edges": [[u, v], ...]}
```
where vertices are numbered ``0 .. n‑1``.

The target problem (ThreeSat) expects an instance of the form
```
{"num_vars": m, "clauses": [[l1, l2, l3], ...]}
```
where each clause contains **exactly three literals** on three distinct
variables.  A literal is a signed integer: ``+v`` means variable ``v`` is
true, ``-v`` means it is false.  Variables are numbered ``1 .. m``.

The classic reduction introduces three Boolean variables for each vertex –
one for each colour – and then enforces:

1. **Each vertex receives at least one colour** – a single 3‑literal clause.
2. **No vertex receives two colours simultaneously** – pairwise “at most one”
   constraints.  These are naturally 2‑literal clauses of the form
   ``(¬x ∨ ¬y)``.
3. **Adjacent vertices cannot share a colour** – for each edge and each
   colour a clause ``(¬x_u_c ∨ ¬x_v_c)``.

The target format, however, forbids clauses with fewer than three literals.
To turn a 2‑literal clause ``(A ∨ B)`` into an equivalent 3‑CNF we use a
standard Tseitin trick: introduce a fresh auxiliary variable ``t`` and add
the two clauses ``(A ∨ B ∨  t)`` and ``(A ∨ B ∨ ¬t)``.  The pair is
logically equivalent to ``(A ∨ B)`` because if ``A ∨ B`` is false then the
two clauses become ``(t)`` and ``(¬t)`` which cannot both be satisfied.

Applying this transformation to every 2‑literal constraint yields a formula
that satisfies the strict 3‑literal requirement while preserving satisfiability.

The reduction runs in time polynomial in the size of the graph (linear in
the number of vertices and edges) and produces a formula with:

* ``3·n`` primary variables (one per vertex‑colour pair)
* ``3·n`` auxiliary variables for the vertex‑pair constraints
* ``3·|E|`` auxiliary variables for the edge‑colour constraints

Thus ``m = 3·n + 3·n + 3·|E| = 6·n + 3·|E|``.

The function ``reduce`` below implements this construction.
"""

from __future__ import annotations

from typing import List, Dict


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to an equivalent ThreeSat instance.

    Parameters
    ----------
    instance: dict
        ``{"n": int, "edges": [[u, v], ...]}`` as described in the problem
        specification.

    Returns
    -------
    dict
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where the
        3‑SAT instance is satisfiable iff the input graph is 3‑colorable.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Helper to map (vertex, colour) -> variable id (1‑based).
    # Colours are indexed 0,1,2.
    def var_id(v: int, colour: int) -> int:
        return v * 3 + colour + 1  # +1 because SAT variables start at 1

    clauses: List[List[int]] = []

    # ------------------------------------------------------------------
    # 1. Each vertex must receive at least one colour.
    # ------------------------------------------------------------------
    for v in range(n):
        clauses.append([var_id(v, 0), var_id(v, 1), var_id(v, 2)])

    # Auxiliary variable counter starts after the primary variables.
    next_aux = 3 * n + 1  # first auxiliary variable id

    # ------------------------------------------------------------------
    # 2. Vertex‑pair (at‑most‑one) constraints.
    #    For each unordered pair of colours (c1, c2) we add the two
    #    3‑clauses (¬x_c1 ∨ ¬x_c2 ∨ t) and (¬x_c1 ∨ ¬x_c2 ∨ ¬t).
    # ------------------------------------------------------------------
    for v in range(n):
        colour_pairs = [(0, 1), (0, 2), (1, 2)]
        for c1, c2 in colour_pairs:
            t = next_aux
            next_aux += 1
            # literals for ¬x_c1 and ¬x_c2
            lit1 = -var_id(v, c1)
            lit2 = -var_id(v, c2)
            clauses.append([lit1, lit2, t])   # positive auxiliary
            clauses.append([lit1, lit2, -t])  # negative auxiliary

    # ------------------------------------------------------------------
    # 3. Edge constraints: adjacent vertices cannot share a colour.
    #    For each edge (u, v) and each colour c we add the same Tseitin pair.
    # ------------------------------------------------------------------
    for u, v in edges:
        for c in range(3):
            t = next_aux
            next_aux += 1
            lit_u = -var_id(u, c)
            lit_v = -var_id(v, c)
            clauses.append([lit_u, lit_v, t])
            clauses.append([lit_u, lit_v, -t])

    num_vars = next_aux - 1  # because next_aux points to the next free id

    return {"num_vars": num_vars, "clauses": clauses}

