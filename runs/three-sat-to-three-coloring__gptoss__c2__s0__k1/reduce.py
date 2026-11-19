"""Reduction from 3-SAT to 3-Coloring.

The source problem (ThreeSat) instance format:
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
    Literals are integers: +v for variable v true, -v for variable v false.

The target problem (ThreeColoring) instance format:
    {"n": n, "edges": [[u, v], ...]}
    Vertices are 0..n-1.

The reduction follows the classic polynomial‑time construction:
  * Three special vertices B (base), T (true), F (false) forming a triangle.
  * For each variable x_i create two vertices p_i (x_i) and n_i (¬x_i).
    Both are adjacent to B and to each other, forcing them to receive the
    colours of T and F (opposite colours).
  * For each clause (ℓ1 ∨ ℓ2 ∨ ℓ3) create a triangle of clause vertices
    c1, c2, c3.  Vertex c_k is adjacent to the vertex representing literal ℓk.
    The clause triangle must be coloured with all three colours; therefore
    at least one of the three literals must be coloured T, i.e. the clause is
    satisfied.

The resulting graph is 3‑colourable iff the original formula is satisfiable.
"""

from typing import Dict, List, Tuple

def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance: dict
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the problem statement.

    Returns
    -------
    dict
        A graph instance with keys ``"n"`` and ``"edges"`` suitable for the
        ThreeColoring problem.
    """
    m = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    edges: List[Tuple[int, int]] = []
    # Helper to add an undirected edge (u,v) with u < v
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        if u > v:
            u, v = v, u
        edges.append((u, v))

    # Special vertices: 0 = Base (B), 1 = True (T), 2 = False (F)
    B, T, F = 0, 1, 2
    add_edge(B, T)
    add_edge(B, F)
    add_edge(T, F)

    # Mapping from literal (+v / -v) to vertex id
    # We'll store two separate lists for positive and negative literals per variable.
    pos_vertex = [None] * (m + 1)  # index by variable number
    neg_vertex = [None] * (m + 1)

    next_id = 3  # next free vertex id after the three specials
    for var in range(1, m + 1):
        pos = next_id
        neg = next_id + 1
        pos_vertex[var] = pos
        neg_vertex[var] = neg
        next_id += 2
        # Connect each literal vertex to Base and to each other
        add_edge(pos, B)
        add_edge(neg, B)
        add_edge(pos, neg)

    # Clause gadgets
    for clause in clauses:
        if len(clause) != 3:
            # According to the specification clauses always have length 3,
            # but we defensively ignore malformed clauses.
            continue
        # Create three new vertices for this clause
        c1 = next_id
        c2 = next_id + 1
        c3 = next_id + 2
        next_id += 3
        # Form a triangle among them
        add_edge(c1, c2)
        add_edge(c2, c3)
        add_edge(c3, c1)
        # Connect each clause vertex to the appropriate literal vertex
        literals = clause
        for lit, cv in zip(literals, (c1, c2, c3)):
            var = abs(lit)
            if var == 0 or var > m:
                # Invalid variable index – skip (should not happen)
                continue
            if lit > 0:
                lit_vertex = pos_vertex[var]
            else:
                lit_vertex = neg_vertex[var]
            add_edge(cv, lit_vertex)

    # Build the final instance dictionary
    n = next_id  # total number of vertices created
    # Convert edge tuples to list format required by the target specification
    edge_list = [[u, v] for (u, v) in edges]
    return {"n": n, "edges": edge_list}

# The module exposes only the reduce function as required.

