"""Reduction from SAT (CNF satisfiability) to Clique.

The source problem is defined in ``problems.py`` as ``Sat`` with the
following instance format:

    {"num_vars": m, "clauses": [[literal, ...], ...]}

Literals are represented as signed integers – a positive integer ``v``
means the variable *v* is true, a negative integer ``-v`` means the
variable *v* is false.  Clauses may be empty, may contain duplicate
 literals, and may even contain both a variable and its negation.

The target problem is ``Clique`` with instance format:

    {"n": n, "edges": [[u, v], ...], "k": k}

The reduction must run in polynomial time and preserve the answer
(``yes`` ↔ ``yes``).  The classic reduction works as follows:

* For each literal in each clause we create a vertex.
* Vertices belonging to the **same clause** are never connected.
* Vertices from **different clauses** are connected unless the two
  literals are contradictory – i.e. they refer to the same variable but
  with opposite signs.
* We ask for a clique of size ``k`` where ``k`` equals the number of
  clauses.  Selecting one vertex from each clause that are all pairwise
  adjacent yields a consistent truth assignment that satisfies every
  clause, and vice‑versa.

Edge cases required by the specification are handled explicitly:

* An instance with **no clauses** is always satisfiable.  We return a
  Clique instance with ``k = 0`` (the problem definition states that
  ``k <= 0`` is always a yes‑instance).
* An instance containing an **empty clause** is unsatisfiable.  We
  return a Clique instance where ``k > n`` (e.g., ``n = 0, k = 1``), which
  is always a no‑instance.

The implementation below follows this description and uses only basic
Python data structures, ensuring polynomial runtime.
"""

from typing import List, Dict, Any


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to a Clique instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` as
        described above.

    Returns
    -------
    dict
        A Clique instance dictionary ``{"n": n, "edges": [...], "k": k}``.
    """

    clauses: List[List[int]] = instance.get("clauses", [])

    # ----- Edge case: formula with no clauses (trivially satisfiable) -----
    if len(clauses) == 0:
        # k <= 0 guarantees a yes‑instance for Clique.
        return {"n": 0, "edges": [], "k": 0}

    # ----- Edge case: formula containing an empty clause (unsatisfiable) -----
    for cl in clauses:
        if len(cl) == 0:
            # Choose n = 0 and k = 1 so that k > n → always no.
            return {"n": 0, "edges": [], "k": 1}

    # ----- Normal reduction -----
    # Create a vertex for each literal occurrence in each clause.
    vertices: List[tuple[int, int]] = []  # (clause_index, literal)
    for ci, cl in enumerate(clauses):
        for lit in cl:
            vertices.append((ci, lit))

    n = len(vertices)
    edges: List[List[int]] = []

    # Add edges between vertices of different clauses unless they are
    # contradictory (same variable, opposite signs).
    for i in range(n):
        ci, li = vertices[i]
        var_i = abs(li)
        sign_i = li > 0
        for j in range(i + 1, n):
            cj, lj = vertices[j]
            if ci == cj:
                # Same clause – never connect.
                continue
            var_j = abs(lj)
            sign_j = lj > 0
            # Contradiction check.
            if var_i == var_j and sign_i != sign_j:
                continue
            edges.append([i, j])

    k = len(clauses)
    return {"n": n, "edges": edges, "k": k}
