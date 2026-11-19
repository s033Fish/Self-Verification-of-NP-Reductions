"""Reduction from NAE-3-SAT to 3-Coloring.

The source problem is ``NaeThreeSat`` (not‑all‑equal 3‑SAT) with instances
of the form ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}`` where each
literal is a string ``"+v"`` (variable *v* true) or ``"-v"`` (variable *v*
false).  The target problem is ``ThreeColoring`` with instances ``{"n": n,
"edges": [[u, v], ...]}`` where vertices are numbered ``0..n-1``.

The classic polynomial‑time reduction works as follows:

* Introduce a special vertex ``c`` (colour ``C``) that will be forced to use
  the third colour.
* For each variable ``i`` (1‑based) create two vertices ``i_T`` and ``i_F``
  representing the truth assignment of the variable.  Connect ``i_T`` to
  ``i_F`` and also connect both of them to ``c``.  This forces each of the
  two vertices to be coloured either ``T`` or ``F`` – they cannot take the
  colour of ``c``.
* For each clause ``(ℓ1, ℓ2, ℓ3)`` add a triangle among the three literal
  vertices.  The literal vertex for ``+i`` is ``i_T`` and for ``-i`` is
  ``i_F``.  A triangle must use all three colours, therefore the three
  literals cannot all be coloured ``T`` nor all ``F`` – exactly the NAE
  condition.

The construction yields a graph with ``1 + 2*m`` vertices and a number of
edges linear in the size of the formula.  It can be built in polynomial
time.

The ``reduce`` function below implements this construction and returns the
target instance.
"""

from typing import Dict, List, Tuple, Set


def reduce(instance: Dict) -> Dict:
    """Reduce a NAE‑3‑SAT instance to a 3‑Coloring instance.

    Parameters
    ----------
    instance: dict
        ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``

    Returns
    -------
    dict
        ``{"n": n, "edges": [[u, v], ...]}`` suitable for the
        ``ThreeColoring`` problem.
    """
    m: int = instance.get("num_vars", 0)
    clauses: List[List[str]] = instance.get("clauses", [])

    # Vertex numbering:
    # 0                 -> the special colour‑C vertex
    # 1,2               -> variable 1 (true, false)
    # 3,4               -> variable 2 (true, false)
    # ...
    # vertex ids are consecutive, total n = 1 + 2*m
    n = 1 + 2 * m

    # Helper to obtain the vertex id for a literal
    def lit_vertex(lit: str) -> int:
        sign = lit[0]
        var = int(lit[1:])  # variables are 1‑based
        # true vertex id for variable v
        true_id = 1 + 2 * (var - 1)
        false_id = true_id + 1
        return true_id if sign == "+" else false_id

    edges_set: Set[Tuple[int, int]] = set()

    # Connect each variable's true/false vertices together and to the base
    base = 0
    for var in range(1, m + 1):
        true_id = 1 + 2 * (var - 1)
        false_id = true_id + 1
        # edge between true and false
        edges_set.add(tuple(sorted((true_id, false_id))))
        # edges to the base vertex to forbid the third colour
        edges_set.add(tuple(sorted((true_id, base))))
        edges_set.add(tuple(sorted((false_id, base))))

    # For each clause add a triangle among the three literal vertices
    for clause in clauses:
        if len(clause) != 3:
            # According to the definition clauses always have length 3,
            # but we guard against malformed input.
            continue
        v1 = lit_vertex(clause[0])
        v2 = lit_vertex(clause[1])
        v3 = lit_vertex(clause[2])
        edges_set.add(tuple(sorted((v1, v2))))
        edges_set.add(tuple(sorted((v1, v3))))
        edges_set.add(tuple(sorted((v2, v3))))

    # Convert set to list of [u, v]
    edges: List[List[int]] = [[u, v] for (u, v) in edges_set]

    return {"n": n, "edges": edges}

