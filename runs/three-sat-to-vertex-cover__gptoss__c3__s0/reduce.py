"""Reduction from 3‑SAT to Vertex Cover.

The source problem is defined by :class:`problems.ThreeSat` and the target
by :class:`problems.VertexCover`.  Both classes expose a static ``is_yes``
method that decides the instance (brute‑force for tiny inputs).

We implement the classic polynomial‑time reduction:

* For each variable *x* we create two vertices ``x_true`` and ``x_false``
  and an edge between them.  Picking exactly one of the two vertices in a
  vertex cover corresponds to setting the variable to true or false.
* For each clause ``(ℓ₁ ∨ ℓ₂ ∨ ℓ₃)`` we create a triangle of three new
  vertices ``c₁, c₂, c₃``.  The three edges of the triangle force the cover
  to contain at least two of the three vertices.
* For each literal ℓᵢ in the clause we add an edge between the clause‑vertex
  ``cᵢ`` and the variable‑vertex representing that literal (``x_true`` for a
  positive literal and ``x_false`` for a negative literal).

With this construction the formula is satisfiable **iff** the resulting
graph has a vertex cover of size ``k = m + 2·|C|`` where ``m`` is the number of
variables and ``|C|`` the number of clauses.

The reduction runs in time linear in the size of the SAT instance, which is
polynomial as required.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, VertexCover


def reduce(instance: Dict) -> Dict:
    """Convert a 3‑SAT instance to a Vertex‑Cover instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"num_vars"`` (int) and ``"clauses"`` (list of
        three‑literal clauses) as specified by :class:`ThreeSat`.

    Returns
    -------
    dict
        A Vertex‑Cover instance with keys ``"n"``, ``"edges"`` and ``"k"``.
    """
    # Validate the source instance – this will raise if malformed.
    ThreeSat.validate(instance)

    m: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    edges: List[List[int]] = []
    # Vertex indexing layout:
    #   0 .. 2*m-1   : variable vertices (even = true, odd = false)
    #   2*m ..       : clause vertices, three per clause.
    # Helper to obtain the vertex index for a literal.
    def lit_vertex(lit: int) -> int:
        var = abs(lit) - 1  # zero‑based variable index
        # true vertex is 2*var, false vertex is 2*var + 1
        return 2 * var if lit > 0 else 2 * var + 1

    # 1. Variable edges (x_true — x_false)
    for var in range(m):
        true_v = 2 * var
        false_v = true_v + 1
        edges.append([true_v, false_v])

    # 2. Clause gadgets
    clause_base = 2 * m  # first index for clause vertices
    for ci, clause in enumerate(clauses):
        # three vertices for this clause
        v1 = clause_base + 3 * ci
        v2 = v1 + 1
        v3 = v1 + 2
        # triangle edges
        edges.append([v1, v2])
        edges.append([v2, v3])
        edges.append([v3, v1])
        # connect each clause vertex to the corresponding literal vertex
        literals = clause  # already length 3
        edges.append([v1, lit_vertex(literals[0])])
        edges.append([v2, lit_vertex(literals[1])])
        edges.append([v3, lit_vertex(literals[2])])

    n_vertices = clause_base + 3 * len(clauses)
    k = m + 2 * len(clauses)

    vc_instance = {"n": n_vertices, "edges": edges, "k": k}
    # Validate target instance before returning (helps catch bugs).
    VertexCover.validate(vc_instance)
    return vc_instance

