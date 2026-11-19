"""Reduction from 3-SAT to Clique.

The source problem is :class:`ThreeSat` defined in ``problems.py``.  An
instance is a dictionary ``{"num_vars": m, "clauses": [[l1, l2, l3], ...]}``
where each clause contains exactly three literals on three distinct
variables.  The target problem is :class:`Clique`.  An instance is a
dictionary ``{"n": n, "edges": [[u, v], ...], "k": k}``.

The classic polynomial‑time reduction creates a vertex for every literal
in every clause.  Two vertices are connected by an edge iff they belong to
different clauses *and* the corresponding literals are not contradictory
+(i.e. they are not a variable and its negation).  The resulting graph has a
clique of size ``#clauses`` iff the original formula is satisfiable – the
clique selects exactly one literal from each clause, and the edge condition
guarantees that the selected literals are mutually consistent.

Edge cases:
* An empty formula (no clauses) is always satisfiable.  We return a graph
  with ``k = 0``; by definition any graph contains a clique of size 0, so
  the answer matches.
* The reduction works for any number of variables; the specification of
  3‑SAT already guarantees ``m >= 3`` when there is at least one clause.

The function validates the input using the problem classes and then
constructs the target instance.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import ThreeSat, Clique


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a 3‑SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary representing a 3‑SAT instance as described in
        :class:`ThreeSat`.

    Returns
    -------
    dict
        A Clique instance ``{"n": n, "edges": edges, "k": k}`` such that
        the original formula is satisfiable iff the graph contains a clique
        of size at least ``k``.
    """

    # Validate the source instance; this will raise InvalidInstance on bad
    # input, matching the expectations of the surrounding framework.
    ThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]  # noqa: F841  (kept for clarity)
    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    # Edge case: empty formula – always yes.  Any graph works with k = 0.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Each literal in each clause becomes a vertex.  Vertex ids are assigned
    # consecutively: clause i (0‑based), literal position j (0‑based) maps to
    # ``i * 3 + j``.
    n = num_clauses * 3
    edges: List[List[int]] = []

    # Pre‑compute vertex ids for convenience.
    def vertex_id(clause_idx: int, lit_idx: int) -> int:
        return clause_idx * 3 + lit_idx

    # Add edges between vertices of different clauses when literals are not
    # complementary.
    for i in range(num_clauses):
        for j in range(i + 1, num_clauses):
            for li_idx, li in enumerate(clauses[i]):
                for lj_idx, lj in enumerate(clauses[j]):
                    # No edge if literals are contradictory (v and -v).
                    if li == -lj:
                        continue
                    u = vertex_id(i, li_idx)
                    v = vertex_id(j, lj_idx)
                    edges.append([u, v])

    # The required clique size is the number of clauses.
    k = num_clauses

    # Validate the target instance before returning to ensure correctness.
    Clique.validate({"n": n, "edges": edges, "k": k})
    return {"n": n, "edges": edges, "k": k}
