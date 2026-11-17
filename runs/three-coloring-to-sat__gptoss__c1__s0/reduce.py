"""Reduction from 3‑Coloring to SAT.

The source problem (ThreeColoring) uses instances of the form

    {"n": <number of vertices>, "edges": [[u, v], ...]}

where vertices are numbered 0 … n‑1 and edges are undirected simple
edges.  The target problem (Sat) expects a CNF formula encoded as

    {"num_vars": m, "clauses": [[lit, ...], ...]}

Variables are numbered 1 … m and a literal is a signed integer:
positive for the variable, negative for its negation.

The classic polynomial‑time reduction introduces three Boolean variables
for each vertex, one for each colour.  Let ``x_{i,c}`` be true iff vertex
``i`` receives colour ``c`` (c ∈ {0,1,2}).  The reduction adds the
following constraints, each translated into one or more CNF clauses:

1. **Each vertex receives at least one colour** – a clause containing the
   three variables of the vertex.
2. **Each vertex receives at most one colour** – for every pair of
   distinct colours a binary clause forbidding both to be true.
3. **Adjacent vertices receive different colours** – for every edge and
   for each colour a binary clause forbidding the two endpoints from
   sharing that colour.

If the original graph is 3‑colourable, the constructed formula is
 satisfiable, and vice‑versa.  The construction runs in time O(n + |E|)
 and uses exactly ``3·n`` variables.
"""

from __future__ import annotations

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeColoring instance to an equivalent SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        ``[u, v]`` pairs).  The instance is assumed to be validated by the
        ``ThreeColoring`` class – the reducer does not perform its own
        validation to keep the implementation lightweight.

    Returns
    -------
    dict
        A SAT instance in the format required by the ``Sat`` class:
        ``{"num_vars": m, "clauses": [[lit, ...], ...]}``.
    """

    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]

    # One variable for each (vertex, colour) pair.
    # Variable numbering starts at 1, so vertex i and colour c maps to
    #   var = i * 3 + c + 1
    num_vars = 3 * n
    clauses: List[List[int]] = []

    # 1. Every vertex gets at least one colour.
    for i in range(n):
        clause = [i * 3 + c + 1 for c in range(3)]
        clauses.append(clause)

    # 2. Every vertex gets at most one colour (pairwise exclusion).
    for i in range(n):
        base = i * 3
        # pairs (0,1), (0,2), (1,2)
        clauses.append([-(base + 1), -(base + 2)])  # ¬x_{i,0} ∨ ¬x_{i,1}
        clauses.append([-(base + 1), -(base + 3)])  # ¬x_{i,0} ∨ ¬x_{i,2}
        clauses.append([-(base + 2), -(base + 3)])  # ¬x_{i,1} ∨ ¬x_{i,2}

    # 3. Adjacent vertices must not share a colour.
    for u, v in edges:
        for c in range(3):
            u_lit = -(u * 3 + c + 1)
            v_lit = -(v * 3 + c + 1)
            clauses.append([u_lit, v_lit])

    return {"num_vars": num_vars, "clauses": clauses}

