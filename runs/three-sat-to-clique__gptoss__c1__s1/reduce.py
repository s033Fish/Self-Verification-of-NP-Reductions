"""Reduction from 3‑SAT to Clique.

The source problem is ``ThreeSat`` with instances of the form::

    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}

where each literal ``li`` is a string ``"+v"`` (variable *v* is true) or
``"-v"`` (variable *v* is false).  Every clause contains exactly three
different variables.

The target problem is ``Clique`` with instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

Vertices are numbered ``0 .. n‑1`` and ``edges`` contains each undirected
edge exactly once.

Standard textbook reduction:

* Create a vertex for each literal occurrence – i.e. for each literal in
  each clause.  Thus we have ``3 * |C|`` vertices where ``|C|`` is the
  number of clauses.
* Connect two vertices with an edge iff they belong to **different**
  clauses *and* the two literals are **not contradictory** (they do not
  refer to the same variable with opposite signs).
* Set ``k`` equal to the number of clauses.

It is well‑known that the constructed graph contains a clique of size
``k`` iff the original 3‑SAT formula is satisfiable.  The construction is
polynomial in the size of the formula.

The implementation below follows exactly this description.  It does not
use any solver – it merely builds the graph representation.
"""

from __future__ import annotations

from typing import Dict, List, Tuple


def _parse_literal(lit: str) -> Tuple[int, str]:
    """Return ``(var, sign)`` where ``sign`` is '+' or '-'."""
    # Literal format is guaranteed by the problem statement.
    sign = lit[0]
    var = int(lit[1:])
    return var, sign


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to an equivalent Clique instance.

    Parameters
    ----------
    instance:
        A dictionary following the ``ThreeSat`` format.

    Returns
    -------
    dict
        A dictionary following the ``Clique`` format such that the
        answer to the Clique instance is *yes* iff the answer to the
        original 3‑SAT instance is *yes*.
    """

    clauses: List[List[str]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Build a list of vertices.  Each vertex corresponds to a literal in a
    # specific clause.  We store the original literal string for later
    # compatibility checks.
    vertices: List[Tuple[int, str]] = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        for lit in clause:
            vertices.append((ci, lit))

    n = len(vertices)
    k = num_clauses  # we need a clique of size equal to the number of clauses

    # Construct edges.
    edges: List[List[int]] = []
    for i in range(n):
        ci, lit_i = vertices[i]
        var_i, sign_i = _parse_literal(lit_i)
        for j in range(i + 1, n):
            cj, lit_j = vertices[j]
            # Vertices from the same clause must not be connected.
            if ci == cj:
                continue
            var_j, sign_j = _parse_literal(lit_j)
            # If they are contradictory (same variable, opposite signs),
            # do not add an edge.
            if var_i == var_j and sign_i != sign_j:
                continue
            edges.append([i, j])

    return {"n": n, "edges": edges, "k": k}

