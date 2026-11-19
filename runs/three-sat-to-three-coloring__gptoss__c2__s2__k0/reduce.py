"""Reduction from 3‑SAT to 3‑Coloring.

The source problem ``ThreeSat`` is described in ``problems.py`` as a
dictionary with keys ``"num_vars"`` and ``"clauses"``.  A clause is a list
of three literals where a literal is an integer ``+v`` (meaning variable
``v`` is true) or ``-v`` (meaning variable ``v`` is false).  The target
problem ``ThreeColoring`` expects a graph given by ``{"n": n, "edges":
[[u, v], ...]}`` where vertices are numbered ``0 .. n-1``.

The classic polynomial‑time reduction constructs a graph that is
3‑colorable iff the formula is satisfiable.  The construction used here
matches the textbook reduction (e.g. Garey & Johnson, *Computers and
Intractability*).  The idea is:

* Create three special vertices that form a triangle.  Their three
  distinct colours will be interpreted as ``TRUE``, ``FALSE`` and a
  ``BASE`` colour that is never used for literals.
* For each variable ``x_i`` add two vertices representing the literal
  ``x_i`` and its negation ``¬x_i``.  Connect the two literals with an
  edge and connect each of them to the ``BASE`` vertex.  Because they are
  adjacent to ``BASE`` they cannot take the base colour; they must be
  coloured either ``TRUE`` or ``FALSE`` and the edge forces them to have
  opposite colours.  Thus a proper 3‑colouring corresponds to a truth
  assignment for the variable.
* For each clause ``(ℓ1, ℓ2, ℓ3)`` add a triangle of three new vertices.
  Connect each vertex of this clause‑triangle to the vertex that
  represents the corresponding literal and also to the ``BASE`` vertex.
  The clause‑triangle can be coloured with three distinct colours only
  if at least one of its incident literals is coloured ``TRUE`` – this
  enforces that the clause is satisfied.

The resulting graph contains the following vertices:

* 0 – ``TRUE`` vertex
* 1 – ``FALSE`` vertex
* 2 – ``BASE`` vertex
* 3,4,… – literal vertices (two per variable)
* … – clause‑triangle vertices (three per clause)

The function ``reduce`` builds this graph and returns it in the format
required by ``ThreeColoring``.  The construction runs in time linear in
the size of the SAT instance, i.e. polynomial time.
"""

from typing import Dict, List, Tuple, Set


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance:
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...]}`` representing the graph.
    """

    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Special vertices: 0 = TRUE, 1 = FALSE, 2 = BASE
    TRUE = 0
    FALSE = 1
    BASE = 2

    edges_set: Set[Tuple[int, int]] = set()

    # Helper to add an undirected edge without duplicates
    def add_edge(u: int, v: int) -> None:
        if u == v:
            return
        a, b = (u, v) if u < v else (v, u)
        edges_set.add((a, b))

    # Triangle among the three special vertices
    add_edge(TRUE, FALSE)
    add_edge(TRUE, BASE)
    add_edge(FALSE, BASE)

    # Create literal vertices for each variable
    # pos_lit_id[i] – vertex id for literal +i (x_i)
    # neg_lit_id[i] – vertex id for literal -i (¬x_i)
    pos_lit_id: List[int] = [0] * (m + 1)
    neg_lit_id: List[int] = [0] * (m + 1)

    next_vid = 3  # next available vertex id after the three specials
    for var in range(1, m + 1):
        pos = next_vid
        neg = next_vid + 1
        next_vid += 2
        pos_lit_id[var] = pos
        neg_lit_id[var] = neg

        # Edge between the literal and its negation (force opposite colours)
        add_edge(pos, neg)
        # Connect both literals to BASE so they cannot take the BASE colour
        add_edge(pos, BASE)
        add_edge(neg, BASE)

    # Clause gadgets
    for clause in clauses:
        # clause is a list of three literals l where l is +v or -v
        # Create three new vertices for the clause triangle
        c_vertices = [next_vid, next_vid + 1, next_vid + 2]
        next_vid += 3
        # Form a triangle among them
        add_edge(c_vertices[0], c_vertices[1])
        add_edge(c_vertices[1], c_vertices[2])
        add_edge(c_vertices[2], c_vertices[0])
        # Connect each clause vertex to the corresponding literal vertex
        for lit, c_vert in zip(clause, c_vertices):
            var = abs(lit)
            if var == 0:
                # Should not happen according to the spec, but guard anyway
                continue
            lit_vertex = pos_lit_id[var] if lit > 0 else neg_lit_id[var]
            add_edge(c_vert, lit_vertex)
            # Also connect to BASE (required for the clause gadget)
            add_edge(c_vert, BASE)

    # Prepare final output
    n = next_vid  # total number of vertices created
    edges = [[u, v] for (u, v) in sorted(edges_set)]
    return {"n": n, "edges": edges}

