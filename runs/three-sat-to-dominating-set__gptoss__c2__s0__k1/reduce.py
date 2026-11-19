"""Reduction from 3-SAT (ThreeSat) to Dominating Set.

The source instance format (ThreeSat) is:
    {"num_vars": m, "clauses": [[l1, l2, l3], ...]}
where each literal li is an integer +v (positive literal) or -v (negated),
with variables numbered 1..m.

The target instance format (DominatingSet) is:
    {"n": n, "edges": [[u, v], ...], "k": k}
with vertices 0..n-1.

Reduction construction (standard NP‑completeness proof):
* For each variable i (1‑based) create three vertices:
    Ti  – representing the literal x_i (true)
    Fi  – representing the literal ¬x_i (false)
    Ai  – an auxiliary vertex.
  Add edges (Ti, Fi), (Ai, Ti), (Ai, Fi).  This forces any dominating set of
  size ≤ m to pick either Ti or Fi (picking Ai would waste a slot and would
  not dominate clause vertices).
* For each clause C_j create a vertex Cj and connect it to the three
  literal vertices that appear in the clause (Ti for a positive literal, Fi
  for a negative one).
* Set k = m (the number of variables).

Correctness sketch:
- Any dominating set D of size ≤ m must contain at least one of Ti, Fi for
  each variable i, otherwise Ai would have to be chosen, leaving a clause
  vertex undominated.
- Consequently D corresponds to a truth assignment (Ti ∈ D ⇔ x_i = True).
- A clause vertex is dominated exactly when at least one of its three
  neighbor literals is in D, i.e., the clause is satisfied.
- Hence D dominates the whole graph iff the formula is satisfiable.

The construction runs in time polynomial in the size of the 3‑SAT instance.
"""

from typing import Dict, List


def reduce(instance: Dict) -> Dict:
    """Reduce a ThreeSat instance to a DominatingSet instance.

    Parameters
    ----------
    instance: dict with keys 'num_vars' and 'clauses'.

    Returns
    -------
    dict with keys 'n', 'edges', 'k' suitable for the DominatingSet problem.
    """
    m: int = instance.get("num_vars", 0)
    clauses: List[List[int]] = instance.get("clauses", [])

    # Vertex indexing:
    # For variable i (1‑based):
    #   Ti = 3*(i-1)
    #   Fi = 3*(i-1) + 1
    #   Ai = 3*(i-1) + 2
    # Clause vertices start after the variable vertices.
    var_vertex_base = 0
    clause_base = 3 * m

    edges: List[List[int]] = []

    # Variable gadgets
    for i in range(1, m + 1):
        Ti = 3 * (i - 1)
        Fi = Ti + 1
        Ai = Ti + 2
        # (Ti, Fi)
        edges.append([Ti, Fi])
        # (Ai, Ti)
        edges.append([Ai, Ti])
        # (Ai, Fi)
        edges.append([Ai, Fi])

    # Clause vertices and connections to literals
    for idx, clause in enumerate(clauses):
        Cj = clause_base + idx
        for lit in clause:
            var = abs(lit)
            if var == 0 or var > m:
                # Invalid literal according to spec – ignore (should not happen)
                continue
            if lit > 0:
                lit_vertex = 3 * (var - 1)  # Ti
            else:
                lit_vertex = 3 * (var - 1) + 1  # Fi
            edges.append([Cj, lit_vertex])

    n = clause_base + len(clauses)
    k = m

    return {"n": n, "edges": edges, "k": k}

# If this file is executed directly, run a simple sanity check.
if __name__ == "__main__":
    # Example: (x1 ∨ ¬x2 ∨ x3) ∧ (¬x1 ∨ x2 ∨ ¬x3)
    example = {
        "num_vars": 3,
        "clauses": [[1, -2, 3], [-1, 2, -3]]
    }
    result = reduce(example)
    import json, sys
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write('\n')
