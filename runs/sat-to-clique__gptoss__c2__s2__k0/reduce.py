"""Reduction from SAT (CNF satisfiability) to Clique.

The source problem is defined by ``Sat`` in *problems.py* with the instance
format:

    {"num_vars": m, "clauses": [[literal, ...], ...]}

where a literal is an integer ``+v`` (variable *v* is true) or ``-v`` (variable
*v* is false).  An empty list of clauses is trivially satisfiable, while a
clause that is the empty list ``[]`` can never be satisfied.

The target problem is ``Clique`` with the instance format:

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction is the classic one used in textbooks:

* For each clause *C_i* and for each literal *ℓ* occurring in *C_i* we create a
  vertex *v_{i,ℓ}*.
* Two vertices coming from **different** clauses are connected by an edge iff
  the corresponding literals are **not contradictory** – i.e. they do not
  refer to the same variable with opposite signs.
* The parameter ``k`` is set to the number of clauses.

It is easy to see that a satisfying assignment picks exactly one literal from
each clause such that the chosen literals are pairwise non‑contradictory.  The
corresponding vertices therefore form a clique of size ``k``.  Conversely, any
clique of size ``k`` must contain one vertex from each clause (vertices from the
same clause are never adjacent) and the literals they represent are mutually
compatible, yielding a satisfying assignment.

The implementation below follows this construction verbatim.  It runs in time
polynomial in the size of the SAT instance – specifically ``O(L^2)`` where ``L``
is the total number of literal occurrences.
"""

from typing import List, Dict, Any


def _compatible(lit1: int, lit2: int) -> bool:
    """Return ``True`` if two literals are not contradictory.

    Two literals contradict each other only when they refer to the same
    variable with opposite signs, e.g. ``+3`` and ``-3``.
    """
    var1, var2 = abs(lit1), abs(lit2)
    if var1 != var2:
        return True
    # Same variable – they are compatible only if they have the same sign.
    return (lit1 > 0) == (lit2 > 0)


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary adhering to the ``Sat`` format described above.

    Returns
    -------
    dict
        A dictionary adhering to the ``Clique`` format such that the answer
        to the returned instance is *yes* iff the answer to the input SAT
        instance is *yes*.
    """
    num_vars = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])
    num_clauses = len(clauses)

    # Edge‑case: formula with no clauses is always satisfiable.  Clique defines
    # k <= 0 as trivially yes, so we return a graph with k = 0.
    if num_clauses == 0:
        return {"n": 0, "edges": [], "k": 0}

    # Build vertices.  We assign a consecutive integer id to each (clause,
    # literal) pair.
    vertex_ids: List[Dict[int, int]] = []  # one dict per clause: literal -> id
    vertices: List[tuple] = []  # (clause_index, literal)
    for ci, clause in enumerate(clauses):
        lit_to_id: Dict[int, int] = {}
        for lit in clause:
            vid = len(vertices)
            lit_to_id[lit] = vid
            vertices.append((ci, lit))
        vertex_ids.append(lit_to_id)

    n = len(vertices)
    edges: List[List[int]] = []

    # Add edges between vertices from different clauses when compatible.
    for i in range(n):
        ci, lit_i = vertices[i]
        for j in range(i + 1, n):
            cj, lit_j = vertices[j]
            if ci == cj:
                # Vertices from the same clause are never adjacent.
                continue
            if _compatible(lit_i, lit_j):
                edges.append([i, j])

    # The target clique size is the number of clauses.
    k = num_clauses

    return {"n": n, "edges": edges, "k": k}

