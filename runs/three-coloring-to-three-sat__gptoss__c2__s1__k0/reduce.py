"""Reduction from 3-Coloring to 3-SAT.

The source problem (ThreeColoring) expects an instance of the form
```
{"n": <num_vertices>, "edges": [[u, v], ...]}
```
where vertices are numbered 0..n-1.

The target problem (ThreeSat) expects an instance of the form
```
{"num_vars": m, "clauses": [[l1, l2, l3], ...]}
```
where each clause contains exactly three literals on three *different*
variables.

The classic reduction introduces a Boolean variable for each vertex‑colour
pair.  For a vertex ``v`` and colour ``c`` (c ∈ {0,1,2}) we use the variable
``X_{v,c}``.  The constraints are:

1. **Each vertex gets at least one colour** – a single 3‑literal clause
   ``(X_{v,0} ∨ X_{v,1} ∨ X_{v,2})``.
2. **A vertex cannot receive two colours** – for each unordered pair of
   colours ``(c1,c2)`` we need ``(¬X_{v,c1} ∨ ¬X_{v,c2})``.
3. **Adjacent vertices cannot share a colour** – for each edge ``(u,v)``
   and colour ``c`` we need ``(¬X_{u,c} ∨ ¬X_{v,c})``.

Constraints (2) and (3) are binary clauses, but the target format only
allows clauses of length three.  A binary clause ``(a ∨ b)`` can be turned
into an equivalent pair of 3‑clauses using a fresh *padding* variable ``p``:

```
(a ∨ b ∨  p) ∧ (a ∨ b ∨ ¬p)
```

If both ``a`` and ``b`` are false, the two clauses force ``p`` and ``¬p``
simultaneously, making the formula unsatisfiable.  If at least one of ``a``
or ``b`` is true, both clauses are satisfied regardless of ``p``.  This
preserves satisfiability while respecting the 3‑literal requirement and
ensuring all three variables in a clause are distinct.

The reduction runs in polynomial time: it creates O(n + |E|) variables and
O(n + |E|) clauses.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to a ThreeSat instance.

    Parameters
    ----------
    instance:
        A dict with keys ``"n"`` (int) and ``"edges"`` (list of [u, v]).

    Returns
    -------
    dict
        An instance of ThreeSat with keys ``"num_vars"`` and ``"clauses"``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Base variables: one for each vertex‑colour pair.
    # Variable IDs start at 1.
    def var_id(v: int, colour: int) -> int:
        """Return the SAT variable number for vertex v and colour.

        Colours are 0,1,2 corresponding to the three colours.
        """
        return v * 3 + colour + 1  # +1 because SAT variables are 1‑based.

    clauses: List[List[int]] = []
    next_var = n * 3 + 1  # first padding variable ID

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clauses.append([var_id(v, 0), var_id(v, 1), var_id(v, 2)])

    # Helper to convert a binary clause (a ∨ b) into two 3‑clauses using a
    # fresh padding variable.
    def add_binary(a: int, b: int) -> None:
        nonlocal next_var
        p = next_var
        next_var += 1
        # Ensure a, b, p are distinct – they are by construction.
        clauses.append([a, b,  p])
        clauses.append([a, b, -p])

    # 2. No vertex may have two colours simultaneously.
    for v in range(n):
        # unordered pairs of colours (0,1), (0,2), (1,2)
        add_binary(-var_id(v, 0), -var_id(v, 1))
        add_binary(-var_id(v, 0), -var_id(v, 2))
        add_binary(-var_id(v, 1), -var_id(v, 2))

    # 3. Adjacent vertices cannot share a colour.
    for u, v in edges:
        add_binary(-var_id(u, 0), -var_id(v, 0))
        add_binary(-var_id(u, 1), -var_id(v, 1))
        add_binary(-var_id(u, 2), -var_id(v, 2))

    num_vars = next_var - 1  # last used variable ID
    return {"num_vars": num_vars, "clauses": clauses}

