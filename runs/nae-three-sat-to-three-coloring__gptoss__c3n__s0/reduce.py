"""Reduction from NAE-3-SAT to 3-Coloring.

The construction follows the classic textbook reduction using a base
triangle representing the three colours (TRUE, FALSE, UNUSED).  For each
variable we create a pair of vertices connected to the UNUSED vertex and
to each other – this forces the pair to take the two colours TRUE and
FALSE, i.e. they represent a truth assignment.  For each clause we add a
triangle of fresh vertices, each adjacent to the literal vertex that
represents the literal in the clause.  The clause triangle must be coloured
with three distinct colours, which is possible iff the three adjacent
literal vertices are not all the same colour (i.e. the clause is not‑all‑
equal).  Hence the resulting graph is 3‑colourable exactly when the
original NAE‑3‑SAT instance is satisfiable.

The reduction runs in polynomial time and produces a graph in the format
required by :class:`ThreeColoring`.
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Set

from problems import NaeThreeSat, ThreeColoring


def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as defined
        by :class:`NaeThreeSat`.

    Returns
    -------
    dict
        A graph instance ``{"n": n, "edges": [[u, v], ...]}`` suitable for
        :class:`ThreeColoring`.
    """
    # Validate the source instance first – this will raise if malformed.
    NaeThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Vertex naming scheme
    # Special vertices for the three colours
    special = ["T", "F", "U"]  # TRUE, FALSE, UNUSED
    vertices: List[str] = []
    vertices.extend(special)

    # Variable vertices: for each variable i we create i_T and i_F
    for i in range(1, m + 1):
        vertices.append(f"{i}_T")
        vertices.append(f"{i}_F")

    # Clause vertices: three fresh vertices per clause
    for ci, _ in enumerate(clauses):
        for j in range(3):
            vertices.append(f"C_{ci}_{j}")

    # Map names to indices
    name_to_idx: Dict[str, int] = {name: idx for idx, name in enumerate(vertices)}

    edges_set: Set[Tuple[int, int]] = set()

    def add_edge(u_name: str, v_name: str) -> None:
        u = name_to_idx[u_name]
        v = name_to_idx[v_name]
        if u == v:
            raise ValueError("self‑loop detected in reduction construction")
        edge = (min(u, v), max(u, v))
        edges_set.add(edge)

    # 1. Base triangle among T, F, U
    add_edge("T", "F")
    add_edge("F", "U")
    add_edge("U", "T")

    # 2. Variable gadgets
    for i in range(1, m + 1):
        ti = f"{i}_T"
        fi = f"{i}_F"
        # Edge between the two literals forces opposite colours (TRUE/FALSE)
        add_edge(ti, fi)
        # Both are adjacent to the UNUSED vertex so they cannot take the UNUSED colour
        add_edge(ti, "U")
        add_edge(fi, "U")

    # 3. Clause gadgets
    for ci, clause in enumerate(clauses):
        clause_vertex_names = []
        for j, lit in enumerate(clause):
            var = abs(lit)
            lit_name = f"{var}_T" if lit > 0 else f"{var}_F"
            cv_name = f"C_{ci}_{j}"
            clause_vertex_names.append(cv_name)
            # Connect clause vertex to the literal vertex
            add_edge(cv_name, lit_name)
        # Connect the three clause vertices in a triangle
        a, b, c = clause_vertex_names
        add_edge(a, b)
        add_edge(b, c)
        add_edge(c, a)

    # Convert edge set to required list format
    edges = [[u, v] for (u, v) in sorted(edges_set)]
    graph_instance = {"n": len(vertices), "edges": edges}

    # Validate the produced target instance
    ThreeColoring.validate(graph_instance)
    return graph_instance

