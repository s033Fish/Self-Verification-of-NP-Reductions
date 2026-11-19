"""Reduction from 3‑SAT to Clique.

The source problem is defined by the ``ThreeSat`` class in ``problems.py``.
An instance is a dictionary ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
where each literal is an integer ``+v`` (variable *v* true) or ``-v`` (variable
*v* false).  The instance is satisfiable iff there exists an assignment that
makes every clause contain at least one true literal.

The target problem is defined by the ``Clique`` class.  An instance is a
dictionary ``{"n": n, "edges": [[u, v], ...], "k": k}`` where the vertices are
``0..n-1`` and ``k`` is the required clique size.  The answer is *yes* iff the
graph contains a clique of size **at least** ``k``.

The classic polynomial‑time reduction works as follows:

* For each clause create a vertex for each of its three literals –
  ``3 * |C|`` vertices in total.
* Connect two vertices with an edge **iff** they belong to *different*
  clauses **and** the corresponding literals are not contradictory (i.e. they
  are not of the form ``v`` and ``-v`` for the same variable).
* Set ``k`` to the number of clauses.

If the original formula is satisfiable, we can pick one true literal from each
clause; the corresponding vertices are pairwise non‑contradictory and thus form
an ``k``‑clique.  Conversely, any ``k``‑clique selects exactly one vertex from
each clause, and the non‑contradiction condition guarantees that the chosen
literal assignments are consistent, yielding a satisfying assignment.

Edge case – an empty formula (no clauses) is always satisfiable.  We output a
trivial Clique instance with ``k = 0`` (always a yes‑instance) and no vertices.

The implementation below follows this description and runs in polynomial time
with respect to the size of the 3‑SAT instance.
"""

from __future__ import annotations

from typing import List, Dict, Any

# Import the problem classes only for optional validation.  The reduction does
# not depend on their internal algorithms, but validating helps catch malformed
# inputs during development.
try:
    from problems import ThreeSat, Clique  # type: ignore
except Exception:  # pragma: no cover – the sandbox always provides problems.py
    ThreeSat = Clique = None  # type: ignore


def _validate_source(instance: Dict[str, Any]) -> None:
    """Validate the 3‑SAT instance using the provided ``ThreeSat`` class.

    The validation is optional; if the class cannot be imported we simply skip
    it.  This function raises ``InvalidInstance`` (defined in ``problems.py``)
    when the instance does not conform to the specification.
    """
    if ThreeSat is not None:
        ThreeSat.validate(instance)  # type: ignore[arg-type]


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to an equivalent Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT formula as described in the module
        docstring.

    Returns
    -------
    dict
        A Clique instance such that ``Clique.is_yes`` returns ``True`` exactly
        when ``ThreeSat.is_yes`` returns ``True`` for the input.
    """
    # Validate the input (optional but cheap).
    _validate_source(instance)

    clauses: List[List[int]] = instance["clauses"]  # type: ignore[index]
    num_clauses = len(clauses)

    # Empty formula – always satisfiable.  Return a trivial yes‑instance for
    # Clique (k = 0 is always yes regardless of n).
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Assign a vertex id to each literal occurrence.  The vertex id encodes the
    # clause index and the position inside the clause.
    # ``vertex_info`` maps vertex id -> literal integer.
    vertex_info: List[int] = []
    for clause in clauses:
        # Each clause is guaranteed to have exactly three literals, but we are
        # defensive and simply iterate over whatever is provided.
        for lit in clause:
            vertex_info.append(lit)

    n = len(vertex_info)  # should be 3 * num_clauses
    k = num_clauses

    # Build edges between vertices from different clauses that are not
    # contradictory.
    edges: List[List[int]] = []
    # Pre‑compute the clause index for each vertex for quick checks.
    clause_of_vertex = [i // 3 for i in range(n)]  # since each clause contributes 3 vertices

    for u in range(n):
        lit_u = vertex_info[u]
        for v in range(u + 1, n):
            # Skip vertices from the same clause.
            if clause_of_vertex[u] == clause_of_vertex[v]:
                continue
            lit_v = vertex_info[v]
            # Contradictory if literals are opposite signs of the same variable.
            if lit_u == -lit_v:
                continue
            edges.append([u, v])

    return {"n": n, "edges": edges, "k": k}

