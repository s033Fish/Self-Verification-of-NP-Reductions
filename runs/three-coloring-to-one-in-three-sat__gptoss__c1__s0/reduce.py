"""Reduction from 3-Coloring to Positive 1-in-3 SAT.

The source problem (ThreeColoring) expects an instance of the form:
    {"n": <number of vertices>, "edges": [[u, v], ...]}
where vertices are numbered 0..n-1.

The target problem (OneInThreeSat) expects an instance of the form:
    {"num_vars": m, "clauses": [[a, b, c], ...]}
where variables are positive integers 1..m and each clause contains three
distinct variables.  A clause is satisfied iff exactly one of its three
variables is assigned True.

Reduction construction
-----------------------
For each vertex *v* we create three variables representing the colour
assigned to *v*:
    col(v,0) – colour 0 (e.g., red)
    col(v,1) – colour 1 (e.g., green)
    col(v,2) – colour 2 (e.g., blue)
These variables are encoded as consecutive integers starting at 1:
    var_id = v * 3 + colour + 1
The clause (col(v,0), col(v,1), col(v,2)) forces exactly one colour per
vertex because a 1‑in‑3 clause requires exactly one true literal.

For each edge (u, v) we must forbid the two endpoints from sharing the
same colour.  The following gadget (standard in textbook reductions) does
the job using only positive literals:

    For each colour c ∈ {0,1,2} introduce a fresh auxiliary variable
    aux_{(u,v),c}.
    Add the three clauses
        (col(u,c), col(v,c), aux_{(u,v),c})
    and a fourth clause linking the auxiliaries
        (aux_{(u,v),0}, aux_{(u,v),1}, aux_{(u,v),2})

Explanation:
    * The clause (col(u,c), col(v,c), aux) is a 1‑in‑3 clause.  If both
      endpoints were coloured c, the clause would have at least two true
      literals – impossible.  If exactly one endpoint uses colour c, the
      auxiliary must be false.  If neither endpoint uses colour c, the
      auxiliary must be true.
    * Because the three auxiliaries appear together in a final clause that
      also requires exactly one true literal, at least one colour must be
      absent from both endpoints.  In a proper 3‑colouring of an edge the
      two endpoints have different colours, so exactly one of the three
      colour‑pairs is absent and the corresponding auxiliary becomes true,
      satisfying the linking clause.  If the endpoints shared a colour the
      construction becomes unsatisfiable.

The reduction runs in polynomial time and produces a formula that is
positive (no negated literals) and uses only clauses of size three.

Edge cases
~~~~~~~~~~
* An empty graph (n = 0) yields a formula with zero variables and zero
  clauses – which is trivially satisfiable, matching the source answer.
* For n ≤ 3 the construction still works; the resulting formula is
  satisfiable because the original graph is always 3‑colourable.

Implementation details
----------------------
The function ``reduce`` receives the source instance dictionary and returns
the target instance dictionary.  Variable identifiers are allocated
sequentially: first the 3n vertex‑colour variables, then fresh auxiliary
variables for each edge‑colour pair.
"""

from __future__ import annotations

from typing import Dict, List

def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑Coloring instance to a Positive 1‑in‑3‑SAT instance.

    Parameters
    ----------
    instance:
        A dictionary with keys ``"n"`` (int) and ``"edges"`` (list of
        two‑element lists).  Vertices are numbered 0..n‑1.

    Returns
    -------
    dict
        A dictionary with keys ``"num_vars"`` and ``"clauses"`` suitable
        for the ``OneInThreeSat`` problem.
    """
    n: int = instance.get("n", 0)
    edges: List[List[int]] = instance.get("edges", [])

    # ------------------------------------------------------------------
    # 1. Vertex colour variables: 3 per vertex, indexed from 1.
    #    id(v, colour) = v * 3 + colour + 1
    # ------------------------------------------------------------------
    def vertex_var(v: int, colour: int) -> int:
        return v * 3 + colour + 1

    clauses: List[List[int]] = []

    # Exactly one colour per vertex.
    for v in range(n):
        clauses.append([
            vertex_var(v, 0),
            vertex_var(v, 1),
            vertex_var(v, 2),
        ])

    # ------------------------------------------------------------------
    # 2. Edge gadgets.
    #    We'll allocate auxiliary variables after the vertex variables.
    # ------------------------------------------------------------------
    next_var = n * 3 + 1  # first free id after vertex vars

    for (u, v) in edges:
        # Create three auxiliary vars for this edge, one per colour.
        aux_vars = []  # list of three ints
        for _ in range(3):
            aux_vars.append(next_var)
            next_var += 1

        # For each colour c, add clause (col(u,c), col(v,c), aux_c)
        for colour in range(3):
            clauses.append([
                vertex_var(u, colour),
                vertex_var(v, colour),
                aux_vars[colour],
            ])

        # Linking clause ensuring exactly one of the three auxiliaries is true.
        clauses.append(aux_vars)

    num_vars = next_var - 1  # because next_var points to the next unused id

    return {"num_vars": num_vars, "clauses": clauses}

