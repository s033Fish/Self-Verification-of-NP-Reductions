"""Reduction from 3-Coloring to 3-SAT.

The source problem (ThreeColoring) expects an instance of the form
```
{"n": n, "edges": [[u, v], ...]}
```
where vertices are numbered 0 … n‑1.  The target problem (ThreeSat) expects
```
{"num_vars": m, "clauses": [[l1, l2, l3], ...]}
```
where each literal is an integer: a positive integer ``v`` denotes the
variable *v* being true, a negative integer ``-v`` denotes *v* being false.
Every clause must contain exactly three *different* variables.

The classic reduction introduces, for each vertex ``i``, three Boolean
variables ``x_{i,1}, x_{i,2}, x_{i,3}`` meaning “vertex *i* receives colour
1/2/3”.  The constraints are:

1. **Exactly one colour per vertex** – encoded as a 3‑literal clause
   ``(x_{i,1} ∨ x_{i,2} ∨ x_{i,3})`` and three pairwise “at most one”
   constraints ``(¬x_{i,c} ∨ ¬x_{i,c'})`` for each unordered pair of colours.

2. **Adjacent vertices differ in colour** – for every edge ``(u, v)`` and each
   colour ``c`` we add ``(¬x_{u,c} ∨ ¬x_{v,c})``.

The latter two families are 2‑literal clauses, but the target format only
allows clauses with *exactly* three literals on three distinct variables.
We transform a clause ``(a ∨ b)`` into the equivalent 3‑CNF pair

```
(a ∨ b ∨ y) ∧ (a ∨ b ∨ ¬y)
```

where ``y`` is a fresh auxiliary variable.  This construction is satisfiable
iff the original 2‑literal clause is satisfied (if ``a ∨ b`` is false the two
new clauses become ``y`` and ``¬y`` simultaneously, which is impossible).

The reduction runs in polynomial time: we create ``3n`` colour variables and
one fresh auxiliary variable for each 2‑literal clause.  The total number of
variables is ``3n + 3n + 3|E| = 6n + 3|E|`` and the number of clauses is
``n + 2·3n + 2·3|E| = n + 6n + 6|E| = 7n + 6|E|``.

Edge cases:
* ``n == 0`` – we return an empty formula (zero variables, zero clauses),
  which is trivially satisfiable and matches the source answer.
* The construction works for any ``n``; graphs with ≤3 vertices are handled
  automatically.

The function ``reduce`` below implements this transformation.
"""

from __future__ import annotations

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeColoring instance to a ThreeSat instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of two‑element
        lists).  The format follows the description in ``problems.py``.

    Returns
    -------
    dict
        A ThreeSat instance ``{"num_vars": m, "clauses": [...]}`` that is
        satisfiable iff the input graph is 3‑colorable.
    """

    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # Trivial case: empty graph – return an empty formula.
    if n == 0:
        return {"num_vars": 0, "clauses": []}

    # Helper to map (vertex, colour) -> variable index (1‑based).
    def var_index(v: int, colour: int) -> int:
        # colour is 0,1,2 corresponding to the three colours.
        return 1 + v * 3 + colour

    clauses: List[List[int]] = []
    next_var: int = 3 * n + 1  # first auxiliary variable index

    # 1. Each vertex receives at least one colour.
    for v in range(n):
        clause = [var_index(v, 0), var_index(v, 1), var_index(v, 2)]
        clauses.append(clause)

    # Helper to replace a 2‑literal clause (a ∨ b) with two 3‑literal clauses
    # using a fresh auxiliary variable.
    def add_2lit_clause(a: int, b: int) -> None:
        nonlocal next_var
        aux = next_var
        next_var += 1
        # (a ∨ b ∨ aux) and (a ∨ b ∨ -aux)
        clauses.append([a, b, aux])
        clauses.append([a, b, -aux])

    # 2. At most one colour per vertex (pairwise constraints).
    for v in range(n):
        # unordered pairs of colours (0,1), (0,2), (1,2)
        pairs = [(0, 1), (0, 2), (1, 2)]
        for c1, c2 in pairs:
            a = -var_index(v, c1)
            b = -var_index(v, c2)
            add_2lit_clause(a, b)

    # 3. Adjacent vertices must not share a colour.
    for u, w in edges:
        for colour in range(3):
            a = -var_index(u, colour)
            b = -var_index(w, colour)
            add_2lit_clause(a, b)

    num_vars = next_var - 1
    return {"num_vars": num_vars, "clauses": clauses}

