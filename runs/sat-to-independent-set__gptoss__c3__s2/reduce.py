"""Reduction from SAT (CNF satisfiability) to Independent Set.

The source problem is defined by ``problems.Sat`` with instances of the form::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

where each literal is an integer ``+v`` (variable ``v`` true) or ``-v``
(variable ``v`` false).  ``literal`` values are guaranteed to be within
``[-m, -1] ∪ [1, m]`` by the validator.

The target problem is ``problems.IndependentSet`` with instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction creates a graph that contains one vertex for every literal
occurrence in the formula.  Vertices belonging to the same clause form a
clique (so at most one literal per clause can be chosen).  Vertices that are
complementary literals (``v`` and ``-v``) are connected across the whole
graph (so a variable cannot be assigned both true and false).  The required
independent set size ``k`` is the number of clauses.

If the formula has no clauses, ``k = 0`` and the graph is empty – the
independent‑set instance is trivially a yes‑instance, matching the SAT
answer.  If a clause is empty, the graph will have fewer vertices than
``k``; consequently ``k > n`` and the independent‑set instance is a no‑
instance, again matching the SAT answer.

The construction runs in time polynomial in the size of the SAT instance.
"""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from problems import Sat, IndependentSet


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an Independent Set instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``Sat`` specification.

    Returns
    -------
    dict
        An ``IndependentSet`` instance such that the answer to the
        Independent Set question is *yes* iff the original SAT formula is
        satisfiable.
    """
    # Validate the SAT instance (may raise InvalidInstance).
    Sat.validate(instance)

    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Assign a vertex id to each literal occurrence.
    # vertex_info stores (literal) for each vertex id.
    vertex_info: List[int] = []  # index is vertex id, value is literal
    clause_vertices: List[List[int]] = []  # per‑clause list of vertex ids

    for clause in clauses:
        current: List[int] = []
        for lit in clause:
            vid = len(vertex_info)
            vertex_info.append(lit)
            current.append(vid)
        clause_vertices.append(current)

    n = len(vertex_info)
    k = num_clauses

    # Build edges using a set to avoid duplicates.
    edge_set: Set[Tuple[int, int]] = set()

    # 1. Edges inside each clause – make a clique.
    for verts in clause_vertices:
        l = len(verts)
        for i in range(l):
            vi = verts[i]
            for j in range(i + 1, l):
                vj = verts[j]
                if vi < vj:
                    edge_set.add((vi, vj))
                else:
                    edge_set.add((vj, vi))

    # 2. Complementary literal edges across the whole graph.
    # Map literal value to list of vertex ids.
    literal_to_vertices: Dict[int, List[int]] = {}
    for vid, lit in enumerate(vertex_info):
        literal_to_vertices.setdefault(lit, []).append(vid)

    # For each variable, connect positive and negative occurrences.
    processed_vars: Set[int] = set()
    for lit in list(literal_to_vertices.keys()):
        var = abs(lit)
        if var in processed_vars:
            continue
        processed_vars.add(var)
        pos = literal_to_vertices.get(var, [])
        neg = literal_to_vertices.get(-var, [])
        for u in pos:
            for v in neg:
                a, b = (u, v) if u < v else (v, u)
                edge_set.add((a, b))

    # Convert edge set to the required list format.
    edges = [[u, v] for (u, v) in edge_set]

    # Assemble the Independent Set instance.
    result = {"n": n, "edges": edges, "k": k}
    # Validate the target instance before returning (helps catch bugs).
    IndependentSet.validate(result)
    return result

