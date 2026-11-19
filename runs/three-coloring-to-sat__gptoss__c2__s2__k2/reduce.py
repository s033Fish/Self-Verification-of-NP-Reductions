"""Reduction from 3-Coloring to SAT.

The source problem is ``ThreeColoring`` whose instances are dictionaries
with the keys ``"n"`` (number of vertices) and ``"edges"`` (a list of
undirected edges).  The target problem is ``Sat`` whose instances are
CNF formulas represented as ``{"num_vars": m, "clauses": [...])``.

For each vertex we introduce three Boolean variables indicating whether
the vertex receives colour 0, 1 or 2.  The reduction adds the standard
constraints:

1. **Exactly‑one colour per vertex** – encoded as one clause requiring at
   least one colour and three binary clauses forbidding two colours at
   the same time.
2. **Adjacent vertices differ** – for every edge (u, v) and every colour c
   we add the clause ``(¬x_{u,c} ∨ ¬x_{v,c})``.

The construction is polynomial in the size of the graph and satisfies
the required correctness property: the produced SAT instance is
 satisfiable iff the original graph is 3‑colourable.

The implementation below follows the specification used by the
``problems.py`` module in the repository.  It does not import that module
directly – the reducer is meant to be a pure function that can be called
by the evaluation harness.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a SAT instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        ``[u, v]`` pairs).  Vertices are numbered ``0`` … ``n‑1``.

    Returns
    -------
    dict
        A SAT instance in the format required by ``problems.py``:
        ``{"num_vars": m, "clauses": [[lit, ...], ...]}`` where each
        literal is an integer ``+v`` (positive) for true or ``-v`` for
        false, with variables numbered starting at ``1``.
    """

    n = instance.get("n", 0)
    edges = instance.get("edges", [])

    # Number of SAT variables: three per vertex.
    num_vars = n * 3
    clauses: List[List[int]] = []

    # Helper to compute the SAT variable index for vertex v and colour c.
    # Colours are 0,1,2.  Variables start at 1.
    def var(v: int, c: int) -> int:
        return v * 3 + c + 1

    # 1. Each vertex gets at least one colour.
    for v in range(n):
        clause = [var(v, 0), var(v, 1), var(v, 2)]
        clauses.append(clause)

        # 2. Each vertex gets at most one colour (pairwise exclusion).
        for c1 in range(3):
            for c2 in range(c1 + 1, 3):
                clauses.append([-var(v, c1), -var(v, c2)])

    # 3. Adjacent vertices must not share the same colour.
    for u, v in edges:
        for c in range(3):
            clauses.append([-var(u, c), -var(v, c)])

    return {"num_vars": num_vars, "clauses": clauses}

