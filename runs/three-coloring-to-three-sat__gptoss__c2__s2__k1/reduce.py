"""Reduction from 3-Coloring to 3-SAT.

The source problem (ThreeColoring) expects an instance of the form

    {"n": n, "edges": [[u, v], ...]}

where vertices are numbered 0 … n‑1.  The target problem (ThreeSat) expects
an instance of the form

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

Each clause must contain exactly three *distinct* literals on distinct
variables.  A literal is a positive integer ``v`` (meaning variable ``v`` is
true) or a negative integer ``-v`` (meaning variable ``v`` is false).

The classic polynomial‑time reduction introduces three Boolean variables for
each vertex – one for each colour – and then encodes the colouring constraints
as a 3‑CNF formula.  Some of those constraints are naturally 2‑clauses (e.g.
``¬R_i ∨ ¬G_i``).  To satisfy the strict 3‑literal requirement we replace each
2‑clause ``(a ∨ b)`` by a pair of 3‑clauses using a fresh auxiliary variable
``y``:

    (a ∨ b ∨  y)   and   (a ∨ b ∨ ¬y)

Both clauses are satisfied exactly when ``a ∨ b`` is satisfied, because if
``a`` and ``b`` are false the two clauses would demand ``y`` to be simultaneously
true and false – impossible.

The reduction runs in polynomial time: it creates O(n + |E|) variables and
O(n + |E|) clauses.
"""

from __future__ import annotations

def reduce(instance: dict) -> dict:
    """Reduce a ThreeColoring instance to a ThreeSat instance.

    Parameters
    ----------
    instance: dict
        ``{"n": int, "edges": List[List[int]]}``

    Returns
    -------
    dict
        ``{"num_vars": int, "clauses": List[List[int]]}``
    """

    n: int = instance.get("n", 0)
    edges = instance.get("edges", [])

    clauses: list[list[int]] = []

    # Mapping: for vertex i (0‑based) we use three variables:
    #   3*i + 1 -> colour 0 (red)
    #   3*i + 2 -> colour 1 (green)
    #   3*i + 3 -> colour 2 (blue)
    # Positive literal means the vertex *has* that colour.

    # 1. Every vertex must receive at least one colour.
    for i in range(n):
        r = 3 * i + 1
        g = 3 * i + 2
        b = 3 * i + 3
        clauses.append([r, g, b])  # (R_i ∨ G_i ∨ B_i)

    # Helper to transform a 2‑clause (a ∨ b) into two 3‑clauses using a fresh
    # auxiliary variable.  The auxiliary variables are numbered after the
    # colour variables.
    aux_counter = 0

    def add_2clause(a: int, b: int) -> None:
        nonlocal aux_counter
        aux_counter += 1
        y = 3 * n + aux_counter  # new variable index
        # (a ∨ b ∨  y) and (a ∨ b ∨ ¬y)
        clauses.append([a, b, y])
        clauses.append([a, b, -y])

    # 2. At most one colour per vertex: pairwise not‑both constraints.
    for i in range(n):
        r = 3 * i + 1
        g = 3 * i + 2
        b = 3 * i + 3
        add_2clause(-r, -g)  # ¬R_i ∨ ¬G_i
        add_2clause(-r, -b)  # ¬R_i ∨ ¬B_i
        add_2clause(-g, -b)  # ¬G_i ∨ ¬B_i

    # 3. Adjacent vertices must not share a colour.
    for u, v in edges:
        ru = 3 * u + 1
        gu = 3 * u + 2
        bu = 3 * u + 3
        rv = 3 * v + 1
        gv = 3 * v + 2
        bv = 3 * v + 3
        add_2clause(-ru, -rv)
        add_2clause(-gu, -gv)
        add_2clause(-bu, -bv)

    num_vars = 3 * n + aux_counter
    return {"num_vars": num_vars, "clauses": clauses}

