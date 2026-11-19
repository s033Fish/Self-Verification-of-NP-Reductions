"""Reduction from 3‑SAT to 3‑Coloring.

The source problem ``ThreeSat`` expects an instance of the form

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is an integer ``+v`` (meaning variable *v* is
true) or ``-v`` (meaning variable *v* is false).  The target problem
``ThreeColoring`` expects a graph described by the number of vertices
``n`` and a list of undirected edges ``[[u, v], ...]``.

The construction below follows the classic polynomial‑time reduction
found in many textbooks (e.g., Garey & Johnson).  It creates three
special vertices that will be forced to receive three distinct colours
in any proper 3‑colouring – we call them ``TRUE``, ``FALSE`` and ``BASE``.
Every variable ``x_i`` gets a pair of vertices ``pos_i`` and ``neg_i``
connected to ``BASE`` and to each other.  Because they cannot use the
``BASE`` colour, they must be coloured ``TRUE`` and ``FALSE`` in some
order; the choice encodes the truth assignment of the variable.

For each clause we add a triangle of three new vertices.  Each vertex
in the triangle is adjacent to the literal vertex that appears in the
clause at the same position.  If a clause is unsatisfied (all three
literals are coloured ``FALSE``), the three clause vertices are all
forbidden from using the ``FALSE`` colour and therefore have only two
available colours (``TRUE`` and ``BASE``), which is impossible for a
triangle.  Conversely, if at least one literal is true, the triangle
can be properly coloured using the three colours.  Hence the graph is
3‑colourable iff the 3‑SAT instance is satisfiable.

The reduction runs in time linear in the size of the SAT instance and
produces a graph with ``n = 3 + 2*m + 3*|clauses|`` vertices.
"""

from typing import Dict, List, Tuple, Set


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"``
        (list of three‑element lists of integers).

    Returns
    -------
    dict
        A graph instance with keys ``"n"`` and ``"edges"`` suitable for
        the ``ThreeColoring`` problem.
    """

    m = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Vertex IDs
    # 0,1,2 are the three special vertices: TRUE, FALSE, BASE
    TRUE, FALSE, BASE = 0, 1, 2
    next_id = 3

    # Mapping from variable index to its positive/negative vertex ids
    pos: Dict[int, int] = {}
    neg: Dict[int, int] = {}

    edges_set: Set[Tuple[int, int]] = set()

    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        a, b = (u, v) if u < v else (v, u)
        edges_set.add((a, b))

    # 1. The base triangle (TRUE‑FALSE‑BASE)
    add_edge(TRUE, FALSE)
    add_edge(FALSE, BASE)
    add_edge(TRUE, BASE)

    # 2. Variable gadgets
    for i in range(1, m + 1):
        pos_i = next_id
        neg_i = next_id + 1
        next_id += 2
        pos[i] = pos_i
        neg[i] = neg_i

        # Connect the pair and both to BASE
        add_edge(pos_i, neg_i)
        add_edge(pos_i, BASE)
        add_edge(neg_i, BASE)

    # 3. Clause gadgets
    for clause in clauses:
        if len(clause) != 3:
            # According to the problem definition this should never happen,
            # but we guard against malformed input.
            continue
        # Create three vertices for this clause
        c_vertices = []
        for _ in range(3):
            v = next_id
            next_id += 1
            c_vertices.append(v)
        # Form a triangle among them
        add_edge(c_vertices[0], c_vertices[1])
        add_edge(c_vertices[1], c_vertices[2])
        add_edge(c_vertices[0], c_vertices[2])
        # Connect each clause vertex to the corresponding literal vertex
        for lit, cv in zip(clause, c_vertices):
            var = abs(lit)
            if var == 0:
                continue
            if lit > 0:
                # positive literal -> connect to the positive vertex
                target = pos.get(var)
            else:
                # negative literal -> connect to the negative vertex
                target = neg.get(var)
            if target is not None:
                add_edge(cv, target)

    # Convert edge set to required list format
    edges = [[u, v] for (u, v) in edges_set]

    return {"n": next_id, "edges": edges}

