"""Reduction from 3-Coloring to 3-SAT.

The source problem (ThreeColoring) instance format:
    {"n": n, "edges": [[u, v], ...]}
where vertices are 0..n-1.

The target problem (ThreeSat) instance format:
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
Each clause must contain exactly three *different* literals on three
different variables.  Literals are represented by signed integers: a
positive integer ``v`` stands for the literal ``+v`` (variable ``v`` is
true) and a negative integer ``-v`` stands for ``-v`` (variable ``v`` is
false).

The reduction is classic: for each vertex we introduce three Boolean
variables representing the three possible colours.  We then encode:

1. **Each vertex receives at least one colour** – a single 3‑literal
   clause ``(x_i ∨ y_i ∨ z_i)``.
2. **Each vertex receives at most one colour** – for every unordered
   pair of colours we need the clause ``(¬x_i ∨ ¬y_i)``.  Because the
   target format requires three literals, we replace each 2‑literal
   clause with a pair of 3‑literal clauses using a fresh auxiliary
   variable ``s``:

       (¬x_i ∨ ¬y_i ∨  s)  ∧  (¬x_i ∨ ¬y_i ∨ ¬s)

   The conjunction of the two clauses is equivalent to the original
   2‑literal clause: if both colours were true we would need ``s`` to be
   simultaneously true and false – impossible.

3. **Adjacent vertices must not share a colour** – for every edge ``(u,
   v)`` and every colour ``c`` we need ``(¬c_u ∨ ¬c_v)``.  The same
   padding trick with a fresh auxiliary variable is used.

All auxiliary variables are unique, ensuring the three‑literal‑per‑clause
requirement and keeping the reduction polynomial‑time.  The number of
variables is ``3*n`` (original colour variables) plus one fresh variable
for each padded 2‑literal clause (two per clause, but each clause uses a
different auxiliary variable).

The function ``reduce`` builds the formula accordingly and returns it
in the required dictionary format.
"""

from __future__ import annotations

from typing import List, Dict, Any


def _add_pairwise_not_clause(
    clauses: List[List[int]], var_a: int, var_b: int, next_var: int
) -> int:
    """Encode the constraint (¬var_a ∨ ¬var_b) using two 3‑literal clauses.

    Returns the next available variable index after adding the auxiliary
    variable.
    """
    aux = next_var
    # (¬a ∨ ¬b ∨  aux)
    clauses.append([-var_a, -var_b, aux])
    # (¬a ∨ ¬b ∨ ¬aux)
    clauses.append([-var_a, -var_b, -aux])
    return next_var + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to a ThreeSat instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (number of vertices) and ``"edges"``
        (list of ``[u, v]`` pairs).

    Returns
    -------
    dict
        A ThreeSat instance with keys ``"num_vars"`` and ``"clauses"``.
    """
    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    clauses: List[List[int]] = []

    # Base colour variables: for vertex i we use 3*i+1, 3*i+2, 3*i+3
    def colour_vars(vertex: int) -> List[int]:
        base = 3 * vertex
        return [base + 1, base + 2, base + 3]

    # 1. Each vertex gets at least one colour (already a 3‑literal clause)
    for v in range(n):
        x, y, z = colour_vars(v)
        clauses.append([x, y, z])

    # Prepare auxiliary variable counter
    next_var = 3 * n + 1  # start after the colour variables

    # 2. At most one colour per vertex using the padding trick
    for v in range(n):
        x, y, z = colour_vars(v)
        for a, b in ((x, y), (x, z), (y, z)):
            next_var = _add_pairwise_not_clause(clauses, a, b, next_var)

    # 3. Adjacent vertices cannot share a colour
    for u, v in edges:
        u_vars = colour_vars(u)
        v_vars = colour_vars(v)
        for cu, cv in zip(u_vars, v_vars):
            next_var = _add_pairwise_not_clause(clauses, cu, cv, next_var)

    num_vars = next_var - 1  # last used variable index

    return {"num_vars": num_vars, "clauses": clauses}

