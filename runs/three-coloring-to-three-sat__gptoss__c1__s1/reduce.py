"""Reduction from 3‑Coloring to 3‑SAT.

The source problem (ThreeColoring) expects an instance of the form

    {"n": int, "edges": [[u, v], ...]}

where vertices are numbered ``0 .. n-1`` and each edge is an unordered
pair of distinct vertices.

The target problem (ThreeSat) expects an instance of the form

    {"num_vars": int, "clauses": [[l1, l2, l3], ...]}

where each clause contains exactly three *different* literals.  A
literal is a signed integer ``+v`` (meaning variable ``v`` is true) or
``-v`` (meaning variable ``v`` is false).  Variables are numbered from
``1`` to ``num_vars``.

The classic reduction introduces three Boolean variables per vertex –
``R_i``, ``G_i`` and ``B_i`` – indicating whether vertex ``i`` receives
the corresponding colour.  The constraints are:

1. **Each vertex receives at least one colour** – a 3‑literal clause
   ``(R_i ∨ G_i ∨ B_i)``.
2. **Each vertex receives at most one colour** – for every unordered
   pair of colours ``(c, d)`` we need the clause ``(¬c_i ∨ ¬d_i)``.
3. **Adjacent vertices cannot share a colour** – for every edge ``(u,
   v)`` and colour ``c`` we need ``(¬c_u ∨ ¬c_v)``.

Constraints (2) and (3) are binary clauses, but the target format
requires exactly three literals per clause.  A binary clause
``(¬x ∨ ¬y)`` is equivalent to the pair of 3‑clauses

    (¬x ∨ ¬y ∨ p) ∧ (¬x ∨ ¬y ∨ ¬p)

where ``p`` is a fresh auxiliary variable that does not appear elsewhere.
If both ``x`` and ``y`` were true, the two clauses would become ``(p)``
and ``(¬p)`` – an immediate contradiction.  Otherwise at least one of
``¬x`` or ``¬y`` is true, satisfying both clauses regardless of the
value of ``p``.  This transformation respects the requirement that the
three literals in each clause are on *different* variables.

Using the transformation above we obtain a 3‑CNF formula that is
 satisfiable iff the original graph is 3‑colourable.  The construction
 runs in time polynomial in ``n + |E|`` and uses a linear number of
 auxiliary variables.

The ``reduce`` function below implements this construction.  It does
not perform any validation of the input – the caller (the benchmark
 framework) guarantees that ``instance`` conforms to the source format.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to an equivalent 3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` and ``"edges"`` as described in the
        problem statement.

    Returns
    -------
    dict
        A 3‑SAT instance ``{"num_vars": m, "clauses": [...]}`` that is
        satisfiable exactly when the input graph is 3‑colourable.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Base variables: three per vertex.  Variable IDs start at 1.
    # For vertex i (0‑based) and colour c in {0,1,2} we use:
    #   var_id = 3 * i + c + 1
    def var_id(vertex: int, colour: int) -> int:
        return 3 * vertex + colour + 1

    clauses: List[List[int]] = []
    next_var = 3 * n + 1  # first auxiliary variable ID

    # 1. Each vertex gets at least one colour.
    for i in range(n):
        clauses.append([var_id(i, 0), var_id(i, 1), var_id(i, 2)])

    # Helper to replace a binary clause (¬a ∨ ¬b) with two 3‑clauses using
    # a fresh auxiliary variable p.
    def add_binary_not(a: int, b: int) -> None:
        nonlocal next_var
        p = next_var
        next_var += 1
        # (¬a ∨ ¬b ∨  p)  and  (¬a ∨ ¬b ∨ -p)
        clauses.append([-a, -b,  p])
        clauses.append([-a, -b, -p])

    # 2. At most one colour per vertex.
    for i in range(n):
        # all unordered pairs of colours {0,1}, {0,2}, {1,2}
        add_binary_not(var_id(i, 0), var_id(i, 1))
        add_binary_not(var_id(i, 0), var_id(i, 2))
        add_binary_not(var_id(i, 1), var_id(i, 2))

    # 3. Adjacent vertices cannot share a colour.
    for u, v in edges:
        for colour in range(3):
            add_binary_not(var_id(u, colour), var_id(v, colour))

    num_vars = next_var - 1  # because next_var points to the next free ID
    return {"num_vars": num_vars, "clauses": clauses}

