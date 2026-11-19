"""Reduction from 3‑SAT to Dominating Set.

The source problem is :class:`ThreeSat` (exactly 3 literals per clause).
The target problem is :class:`DominatingSet`.

For a 3‑SAT instance with ``m`` variables and ``t`` clauses we build a graph
containing three vertices for each variable (a triangle) and one vertex for
each clause.  The variable triangle consists of the vertices representing the
literal *true*, the literal *false* and a centre vertex.  Selecting either the
true‑ or false‑literal vertex dominates the whole triangle, mimicking the
choice of a truth value for the variable.  The centre vertex is provided so
that the triangle can be dominated by a single vertex (any of the three).

Each clause vertex is adjacent to the three literal vertices that appear in
the clause.  Consequently a clause vertex is dominated iff at least one of its
literals is chosen in the dominating set – i.e. the clause is satisfied.

We set the budget ``k = m + t``.  If the formula is satisfiable we can pick
one vertex from each variable triangle according to a satisfying assignment
and, for every clause, pick one literal that makes the clause true.  This
produces a dominating set of size at most ``m + t``.  Conversely, any
dominating set of size at most ``m + t`` must contain at least one vertex from
each variable triangle (otherwise the centre vertex would be undominated) and
at least one literal for each clause, from which a satisfying assignment can
be extracted.

The implementation follows the description above and returns an instance of
the target problem in the format required by ``problems.py``.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import ThreeSat, DominatingSet


def _add_edge(edges_set: set[Tuple[int, int]], u: int, v: int) -> None:
    """Add an undirected edge to ``edges_set``.

    ``edges_set`` stores edges as ordered tuples ``(min, max)`` to avoid
    duplicates and to satisfy the validation rules of ``DominatingSet``.
    """

    if u == v:
        raise AssertionError("self‑loops are not allowed in the reduction")
    a, b = (u, v) if u < v else (v, u)
    edges_set.add((a, b))


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Dominating‑Set instance.

    The function validates the input using :meth:`ThreeSat.validate` and then
    constructs the graph described in the module docstring.  It returns a
    dictionary ``{"n": n, "edges": edges, "k": k}`` suitable for the target
    problem.
    """

    # Validate the source instance.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    t: int = len(clauses)

    # Mapping from a symbolic vertex name to its integer id.
    name_to_id: Dict[str, int] = {}
    vertex_names: List[str] = []

    # Variable gadget vertices.
    for i in range(1, m + 1):
        for suffix in ("_T", "_F", "_C"):
            name = f"v{i}{suffix}"
            name_to_id[name] = len(vertex_names)
            vertex_names.append(name)

    # Clause vertices.
    for j in range(t):
        name = f"cl{j}"
        name_to_id[name] = len(vertex_names)
        vertex_names.append(name)

    n = len(vertex_names)
    edges_set: set[Tuple[int, int]] = set()

    # Build variable triangles.
    for i in range(1, m + 1):
        true_id = name_to_id[f"v{i}_T"]
        false_id = name_to_id[f"v{i}_F"]
        centre_id = name_to_id[f"v{i}_C"]
        _add_edge(edges_set, true_id, false_id)
        _add_edge(edges_set, true_id, centre_id)
        _add_edge(edges_set, false_id, centre_id)

    # Connect clause vertices to the appropriate literal vertices.
    for j, clause in enumerate(clauses):
        clause_id = name_to_id[f"cl{j}"]
        for lit in clause:
            var = abs(lit)
            lit_name = f"v{var}_T" if lit > 0 else f"v{var}_F"
            lit_id = name_to_id[lit_name]
            _add_edge(edges_set, clause_id, lit_id)

    # Convert the edge set to the list format required by the problem.
    edges: List[List[int]] = [[u, v] for (u, v) in sorted(edges_set)]

    k = m + t

    result = {"n": n, "edges": edges, "k": k}
    # Validate the target instance before returning.
    DominatingSet.validate(result)
    return result

