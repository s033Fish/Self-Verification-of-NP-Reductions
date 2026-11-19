"""Reduction from 3-SAT to Vertex Cover.

The source problem is defined in ``problems.py`` as ``ThreeSat`` with the
instance format:

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``l`` is an integer ``+v`` (meaning variable ``v`` is true)
or ``-v`` (meaning variable ``v`` is false).  A formula is satisfiable iff there
exists an assignment to the ``m`` variables that makes every clause true.

The target problem is ``VertexCover`` with the instance format:

    {"n": n, "edges": [[u, v], ...], "k": k}

The instance is a yes‑instance iff the graph has a vertex cover of size at most
``k``.

We implement the classic polynomial‑time reduction:

* **Variable gadget** – for each variable ``x_i`` we create two vertices
  ``v_i_true`` and ``v_i_false`` and add the edge ``(v_i_true, v_i_false)``.
  In any vertex cover of size ``m + 2·|C|`` (see below) exactly one of the two
  vertices must be chosen; picking ``v_i_true`` corresponds to setting ``x_i``
  to true, picking ``v_i_false`` corresponds to false.

* **Clause gadget** – for each clause ``C = (ℓ1 ∨ ℓ2 ∨ ℓ3)`` we add three new
  vertices ``c_1, c_2, c_3`` forming a triangle (edges between each pair).
  Additionally we connect each ``c_k`` to the variable vertex that represents
  the literal ``ℓk`` (i.e. to ``v_i_true`` if ``ℓk`` is ``+i`` and to
  ``v_i_false`` if ``ℓk`` is ``-i``).

If a clause is satisfied by some literal, the corresponding variable vertex is
included in the cover, thereby covering the edge to the clause vertex.  The
triangle can then be covered by selecting the *other two* clause vertices.
Thus a satisfying assignment yields a vertex cover of size
``m + 2·|clauses|``.

Conversely, any vertex cover of size at most ``m + 2·|clauses|`` must select
exactly one vertex from each variable edge (otherwise we would exceed the
budget) and at least two vertices from each clause triangle.  The uncovered
clause vertex corresponds to a literal whose variable vertex is selected, so
that literal is true.  Hence the assignment satisfies every clause.

The reduction runs in time linear in the size of the 3‑SAT instance.
"""

from typing import Dict, List, Tuple


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Vertex Cover instance.

    Parameters
    ----------
    instance: dict
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...], "k": k}`` suitable for the
        ``VertexCover`` problem.
    """

    m = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Assign vertex IDs.
    # Variable vertices: for each i in 1..m we create two vertices.
    # true_id = 2*(i-1), false_id = 2*(i-1) + 1
    var_true: List[int] = []   # index i-1 -> vertex id for +i
    var_false: List[int] = []  # index i-1 -> vertex id for -i
    for i in range(1, m + 1):
        true_id = len(var_true) * 2
        false_id = true_id + 1
        var_true.append(true_id)
        var_false.append(false_id)

    # After variable vertices, clause vertices start.
    clause_vertex_start = len(var_true) * 2
    clause_vertices: List[Tuple[int, int, int]] = []  # three vertex ids per clause

    edges_set = set()  # store (u, v) with u < v to avoid duplicates

    # Variable edges (v_i_true, v_i_false)
    for i in range(m):
        u = var_true[i]
        v = var_false[i]
        edges_set.add((min(u, v), max(u, v)))

    # Process each clause
    for clause_idx, clause in enumerate(clauses):
        # Each clause must have exactly three literals; we trust the input.
        # Create three new vertices.
        base = clause_vertex_start + 3 * clause_idx
        c1, c2, c3 = base, base + 1, base + 2
        clause_vertices.append((c1, c2, c3))

        # Triangle edges among clause vertices
        for (u, v) in ((c1, c2), (c1, c3), (c2, c3)):
            edges_set.add((min(u, v), max(u, v)))

        # Connect each clause vertex to the appropriate variable vertex.
        for lit, cv in zip(clause, (c1, c2, c3)):
            var = abs(lit) - 1  # zero‑based index
            if var < 0 or var >= m:
                # If the literal refers to a non‑existent variable, we still
                # create a dummy isolated vertex for safety.  This situation
                # should not happen for well‑formed inputs, but handling it
                # avoids crashes.
                continue
            if lit > 0:
                # positive literal => connect to true vertex
                target = var_true[var]
            else:
                # negative literal => connect to false vertex
                target = var_false[var]
            edges_set.add((min(cv, target), max(cv, target)))

    n = clause_vertex_start + 3 * len(clauses)
    edges = [[u, v] for (u, v) in sorted(edges_set)]
    k = m + 2 * len(clauses)

    return {"n": n, "edges": edges, "k": k}

