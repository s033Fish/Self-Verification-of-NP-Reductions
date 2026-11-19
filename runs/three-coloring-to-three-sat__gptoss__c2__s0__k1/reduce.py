"""Reduction from 3-Coloring to 3-SAT.

The source problem (ThreeColoring) expects an instance of the form::

    {"n": int, "edges": [[u, v], ...]}

where vertices are numbered ``0..n-1`` and each edge is an undirected
pair of distinct vertices.  The target problem (ThreeSat) expects a CNF
formula where every clause contains **exactly three literals on three
different variables**.  Literals are encoded as signed integers: ``+v``
means variable ``v`` is true, ``-v`` means it is false.  Variables are
numbered from ``1``.

The classic polynomial‑time reduction introduces three Boolean variables
``v_R, v_G, v_B`` for each vertex ``v`` indicating which colour is chosen.
We must encode the following constraints:

* **Exactly one colour per vertex** – at least one of the three colour
  variables is true and no two are true simultaneously.
* **Adjacent vertices have different colours** – for every edge ``(u, v)``
  and every colour ``c`` the clause ``¬u_c ∨ ¬v_c`` must hold.

The *at‑least‑one* constraints already have three literals, but the
*at‑most‑one* and edge‑difference constraints are binary clauses.  The
target format does not allow clauses of length two, so each binary clause
``(a ∨ b)`` is replaced by the pair of clauses ``(a ∨ b ∨ y)`` and
``(a ∨ b ∨ ¬y)`` where ``y`` is a fresh auxiliary variable that does not
appear elsewhere.  The conjunction of the pair is equivalent to the
original binary clause because ``y ∨ ¬y`` is a tautology.

The reduction runs in time polynomial in the size of the graph and
produces a formula that is satisfiable iff the original graph is
3‑colourable.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes only for validation (optional).  The sandbox
# guarantees that ``problems.py`` is present in the working directory.
try:
    from problems import ThreeColoring, ThreeSat
except Exception:  # pragma: no cover – validation is best‑effort only
    ThreeColoring = None  # type: ignore
    ThreeSat = None  # type: ignore


def _add_binary_clause(lit1: int, lit2: int, clauses: List[List[int]], next_var: int) -> int:
    """Replace a binary clause ``(lit1 ∨ lit2)`` with two 3‑literal clauses.

    ``next_var`` is the index of a fresh auxiliary variable.  The function
    appends the two new clauses to ``clauses`` and returns the next free
    variable index after the auxiliary variable has been consumed.
    """
    aux = next_var
    # (lit1 ∨ lit2 ∨ aux) ∧ (lit1 ∨ lit2 ∨ ¬aux)
    clauses.append([lit1, lit2, aux])
    clauses.append([lit1, lit2, -aux])
    return next_var + 1


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑Coloring instance to an equivalent 3‑SAT instance.

    The returned dictionary follows the format required by ``ThreeSat``:
    ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``.
    """
    # Optional validation – if the class is available we use its validator.
    if ThreeColoring is not None:
        ThreeColoring.validate(instance)

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # Mapping: (vertex, colour) -> variable number (1‑based).
    # Colours are indexed 0,1,2.
    def var(v: int, colour: int) -> int:
        return v * 3 + colour + 1

    clauses: List[List[int]] = []
    next_aux = 3 * n + 1  # first auxiliary variable after the base ones

    # 1. At least one colour for each vertex (already a 3‑literal clause).
    for v in range(n):
        clauses.append([var(v, 0), var(v, 1), var(v, 2)])

    # 2. At most one colour per vertex – for each pair of colours add a binary
    #    clause and replace it with two 3‑literal clauses using an aux variable.
    for v in range(n):
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                lit1 = -var(v, c1)
                lit2 = -var(v, c2)
                next_aux = _add_binary_clause(lit1, lit2, clauses, next_aux)

    # 3. Edge constraints – adjacent vertices cannot share the same colour.
    for u, w in edges:
        for c in range(3):
            lit1 = -var(u, c)
            lit2 = -var(w, c)
            next_aux = _add_binary_clause(lit1, lit2, clauses, next_aux)

    num_vars = next_aux - 1  # the last used variable index

    # Optional validation of the produced SAT instance.
    if ThreeSat is not None:
        # ``validate`` expects the exact keys "num_vars" and "clauses".
        ThreeSat.validate({"num_vars": num_vars, "clauses": clauses})

    return {"num_vars": num_vars, "clauses": clauses}

