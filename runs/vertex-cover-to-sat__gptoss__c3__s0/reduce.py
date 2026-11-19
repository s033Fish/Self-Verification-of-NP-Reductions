"""Reduction from Vertex Cover to SAT.

The source problem is :class:`VertexCover` whose instances are dictionaries
with keys "n" (number of vertices), "edges" (list of [u, v]) and
"k" (maximum allowed size of the cover).

The target problem is :class:`Sat` whose instances consist of "num_vars"
and "clauses" where each clause is a list of integer literals using the
convention +v for a true variable v and -v for a false variable.

We construct a SAT formula that is satisfiable iff the given graph has a
vertex‑cover of size at most k.  The construction works in polynomial time
and uses a standard “position” encoding:

* For each position p (0 <= p < k) we create a *selection* variable
  x_{p, v} for every real vertex v (0 <= v < n).  Selecting a vertex in any
  position means that vertex belongs to the cover.
* To allow the cover to contain *fewer* than k vertices we add a dedicated
  *dummy* variable d_p for each position.  Dummies are isolated (they do not
  appear in any edge clause) and can be chosen to fill unused positions.

Constraints encoded as CNF clauses:

1. **Exactly one choice per position** – a clause requiring at least one of
   the x variables or the dummy to be true, plus pairwise mutual‑exclusion
   clauses to forbid two true choices in the same position.
2. **Vertex used at most once** – for each real vertex v and each pair of
   distinct positions p < q we add the clause ¬x_{p,v} ∨ ¬x_{q,v}.
3. **Edge coverage** – for every edge (u, v) we add a clause that at least
   one endpoint is selected in *some* position:
   x_{0,u} ∨ x_{1,u} ∨ … ∨ x_{k‑1,u} ∨ x_{0,v} ∨ … ∨ x_{k‑1,v}.

The resulting formula uses k * (n + 1) variables and a number of clauses
that is polynomial in n and k.  The reduction also handles the edge
cases described in the problem statements:

* k < 0 – always unsatisfiable (we return a formula containing an empty
  clause).
* k >= n – always satisfiable (the empty formula with num_vars = 0).
* k == 0 – satisfiable iff the graph has no edges.

The function ``reduce`` below implements this construction.
"""

from __future__ import annotations

from typing import List, Dict

def _var_id(position: int, vertex: int, n: int) -> int:
    """Return a fresh variable identifier for ``x_{position, vertex}``.

    Variables are numbered starting at 1.  The layout is:
    * first ``k * n`` variables correspond to real vertex selections,
    * the next ``k`` variables correspond to the dummy variables ``d_p``.
    """
    return position * n + vertex + 1


def _dummy_id(position: int, n: int, k: int) -> int:
    """Identifier for the dummy variable of a given position.

    It follows the block of real‑vertex variables.
    """
    return k * n + position + 1


def reduce(instance: Dict) -> Dict:
    """Reduce a VertexCover instance to a SAT instance.

    The returned dictionary follows the format required by ``Sat``:
    {"num_vars": m, "clauses": [[l1, l2, ...], ...]}.
    """
    n: int = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k: int = instance["k"]

    # Edge cases handled directly.
    if k < 0:
        # Unsatisfiable formula: a single empty clause.
        return {"num_vars": 0, "clauses": [[]]}
    if k >= n:
        # Always satisfiable – empty formula.
        return {"num_vars": 0, "clauses": []}
    if k == 0:
        # Satisfiable only when there are no edges.
        if not edges:
            return {"num_vars": 0, "clauses": []}
        else:
            return {"num_vars": 0, "clauses": [[]]}

    # General case 0 < k < n.
    clauses: List[List[int]] = []
    num_vars = k * (n + 1)  # n real vars per position + 1 dummy per position

    # 1. Exactly one choice per position (at least one, plus at‑most‑one).
    for p in range(k):
        # At least one variable true in this position.
        at_least_one: List[int] = [_var_id(p, v, n) for v in range(n)]
        at_least_one.append(_dummy_id(p, n, k))
        clauses.append(at_least_one)

        # Pairwise at‑most‑one among real vertices.
        for v in range(n):
            for w in range(v + 1, n):
                clauses.append([-_var_id(p, v, n), -_var_id(p, w, n)])
            # Real vertex vs dummy.
            clauses.append([-_var_id(p, v, n), -_dummy_id(p, n, k)])

    # 2. A real vertex cannot appear in two different positions.
    for v in range(n):
        for p in range(k):
            for q in range(p + 1, k):
                clauses.append([-_var_id(p, v, n), -_var_id(q, v, n)])

    # 3. Edge coverage clauses.
    for (u, v) in edges:
        clause: List[int] = []
        for p in range(k):
            clause.append(_var_id(p, u, n))
            clause.append(_var_id(p, v, n))
        clauses.append(clause)

    return {"num_vars": num_vars, "clauses": clauses}

