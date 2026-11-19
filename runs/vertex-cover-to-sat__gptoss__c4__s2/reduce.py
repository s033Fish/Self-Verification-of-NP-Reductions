"""Reduction from Vertex Cover to SAT (polynomial in input size).

We first discard isolated vertices because they never need to be chosen.  Let
R be the set of vertices that appear in at least one edge; let r = |R|.  The
instance is equivalent to a Vertex Cover instance on the induced subgraph
with vertices R and the same edges, and the same bound k (but we can cap k at r).

For the reduced instance we create a Boolean variable x_i for each vertex i in R
(renumbered 0..r-1).  Edge clauses are (x_u ∨ x_v).

To enforce the cardinality "at most k" we use the classic order (sequential
counter) encoding which needs O(r·k) auxiliary variables and clauses.  Since r
is at most twice the number of edges, the total size is polynomial in the
input representation.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from problems import VertexCover, Sat


def _var_x(i: int) -> int:
    """SAT variable for vertex i (0‑based after compression)."""
    return i + 1


def _var_a(i: int, j: int, r: int, k: int) -> int:
    """Auxiliary variable a_{i,j} for the sequential counter.

    i is 1‑based (first vertex), j in 0..k.  Variables are numbered after the
    r vertex variables.
    """
    offset = r
    return offset + (i - 1) * (k + 1) + j + 1


def _compress(instance: Dict) -> Tuple[int, List[Tuple[int, int]], int]:
    """Return (r, compressed_edges, k') for the instance.

    Vertices that never appear in an edge are removed.  k' = min(k, r).
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    # collect vertices that appear in edges
    used = set()
    for u, v in edges:
        used.add(u)
        used.add(v)
    mapping = {v: i for i, v in enumerate(sorted(used))}
    r = len(mapping)
    comp_edges = [(mapping[u], mapping[v]) for u, v in edges]
    k_prime = k
    if k_prime > r:
        k_prime = r
    return r, comp_edges, k_prime


def reduce(instance: Dict) -> Dict:
    VertexCover.validate(instance)
    n = instance["n"]
    k = instance["k"]
    edges = instance["edges"]

    # Negative k -> unsatisfiable.
    if k < 0:
        unsat = {"num_vars": 1, "clauses": [[]]}
        Sat.validate(unsat)
        return unsat

    # No edges -> always yes.
    if not edges:
        # trivial satisfiable formula (no clauses).
        triv = {"num_vars": 0, "clauses": []}
        Sat.validate(triv)
        return triv

    # Compress graph.
    r, comp_edges, k_prime = _compress(instance)

    # If k' >= r the bound is vacuous.
    if k_prime >= r:
        # Only need edge clauses (variables for each vertex).
        num_vars = r
        clauses = []
        for u, v in comp_edges:
            clauses.append([_var_x(u), _var_x(v)])
        sat_inst = {"num_vars": num_vars, "clauses": clauses}
        Sat.validate(sat_inst)
        return sat_inst

    # General case: 0 <= k' < r.
    num_vars = r + r * (k_prime + 1)
    clauses: List[List[int]] = []

    # Edge constraints.
    for u, v in comp_edges:
        clauses.append([_var_x(u), _var_x(v)])

    # Sequential counter encoding (order encoding) for at‑most‑k'.
    for i in range(1, r + 1):
        for j in range(0, k_prime + 1):
            a_ij = _var_a(i, j, r, k_prime)
            x_i_1 = _var_x(i - 1)
            # a_{i,j} -> a_{i-1,j}
            if i > 1:
                a_i1_j = _var_a(i - 1, j, r, k_prime)
                clauses.append([-a_ij, a_i1_j])
            # a_{i,j} -> (¬x_{i-1} ∨ a_{i-1,j-1})
            if j >= 1:
                if i > 1:
                    a_i1_j1 = _var_a(i - 1, j - 1, r, k_prime)
                    clauses.append([-a_ij, -x_i_1, a_i1_j1])
                else:
                    clauses.append([-a_ij, -x_i_1])
            else:
                # j == 0 forces x_{i-1} false
                clauses.append([-a_ij, -x_i_1])
            # a_{i-1,j} -> (x_{i-1} ∨ a_{i,j})
            if i > 1:
                a_i1_j = _var_a(i - 1, j, r, k_prime)
                clauses.append([-a_i1_j, x_i_1, a_ij])
            # a_{i-1,j-1} -> (¬x_{i-1} ∨ a_{i,j})
            if j >= 1 and i > 1:
                a_i1_j1 = _var_a(i - 1, j - 1, r, k_prime)
                clauses.append([-a_i1_j1, -x_i_1, a_ij])

    # Force a_{r,k'} true.
    clauses.append([_var_a(r, k_prime, r, k_prime)])

    sat_inst = {"num_vars": num_vars, "clauses": clauses}
    Sat.validate(sat_inst)
    return sat_inst

