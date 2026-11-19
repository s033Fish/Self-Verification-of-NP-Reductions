"""Reduction from SAT (CNF satisfiability) to Clique.

The source problem is defined in ``problems.py`` as ``Sat`` with instances of the form::

    {"num_vars": m, "clauses": [[literal, ...], ...]}

where each ``literal`` is an integer ``+v`` (positive) meaning variable *v* is true,
or ``-v`` meaning variable *v* is false.  A clause is a list of literals (it may be
empty, may contain duplicates, and may even contain both a variable and its
negation).  The formula is satisfiable iff there exists an assignment to the
variables that makes every clause contain at least one true literal.

The target problem is ``Clique`` with instances of the form::

    {"n": n, "edges": [[u, v], ...], "k": k}

where vertices are numbered ``0`` … ``n-1`` and ``edges`` is a list of unordered
pairs.  The answer is *yes* iff the graph contains a clique of size **at least**
``k``.

The classic polynomial‑time reduction creates a vertex for every literal that
appears in a clause.  Vertices belonging to the same clause are never adjacent.
Vertices from different clauses are adjacent unless the corresponding literals
are contradictory (i.e. they refer to the same variable with opposite signs).
If the CNF has ``c`` clauses, we ask for a clique of size ``c``.  A satisfying
assignment picks exactly one literal from each clause, and those literals are
pairwise non‑contradictory, forming a clique.  Conversely, a clique of size ``c``
must contain one vertex from each clause and therefore yields a satisfying
assignment.

Edge cases are handled explicitly:

* **No clauses** – the formula is trivially satisfiable.  We return a graph with
  ``k = 0`` (always a yes‑instance for Clique).
* **An empty clause** – the formula is unsatisfiable.  We return a graph where
  ``k > n`` (e.g., ``n = 0, k = 1``) which is a guaranteed no‑instance.

The implementation below follows this description and runs in time polynomial
in the size of the SAT instance (linear in the number of literals plus the
quadratic number of potential edges between different clauses).
"""

from __future__ import annotations

from typing import Dict, List

def _contradict(lit1: int, lit2: int) -> bool:
    """Return ``True`` if *lit1* and *lit2* are contradictory.

    Two literals contradict each other when they refer to the same variable
    with opposite signs, i.e. ``lit1 == -lit2``.
    """
    return lit1 == -lit2


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as described
        in the problem statement.

    Returns
    -------
    dict
        A Clique instance ``{"n": n, "edges": [...], "k": k}`` that is a
        yes‑instance iff the input SAT instance is satisfiable.
    """

    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge case: formula contains an empty clause -> unsatisfiable.
    if any(len(cl) == 0 for cl in clauses):
        # Return a graph with n = 0 and k = 1 (k > n) which is always a no‑instance.
        return {"n": 0, "edges": [], "k": 1}

    # Edge case: no clauses -> trivially satisfiable.
    if num_clauses == 0:
        # k = 0 is always yes for Clique.
        return {"n": 0, "edges": [], "k": 0}

    # Map each (clause_index, literal_index) to a unique vertex id.
    vertex_id: List[List[int]] = []  # parallel structure to clauses
    current_id = 0
    for cl in clauses:
        ids_for_clause = []
        for _ in cl:
            ids_for_clause.append(current_id)
            current_id += 1
        vertex_id.append(ids_for_clause)

    n = current_id
    edges_set = set()

    # Build edges between vertices of different clauses when literals are not contradictory.
    for i in range(num_clauses):
        for j in range(i + 1, num_clauses):
            # Compare each literal in clause i with each literal in clause j.
            for idx_i, lit_i in enumerate(clauses[i]):
                for idx_j, lit_j in enumerate(clauses[j]):
                    if not _contradict(lit_i, lit_j):
                        u = vertex_id[i][idx_i]
                        v = vertex_id[j][idx_j]
                        # Store edges with smaller id first to avoid duplicates.
                        if u < v:
                            edges_set.add((u, v))
                        else:
                            edges_set.add((v, u))

    # Convert set to required list format.
    edges: List[List[int]] = [[u, v] for (u, v) in edges_set]

    # The target clique size is the number of clauses.
    k = num_clauses

    return {"n": n, "edges": edges, "k": k}

