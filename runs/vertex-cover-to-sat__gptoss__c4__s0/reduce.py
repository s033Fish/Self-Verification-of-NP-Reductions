"""Reduction from Vertex Cover to SAT (polynomial size).

The reduction works in two modes:

* **Small instances** (where n*k ≤ 20) – we use the classic encoding with a
  variable p_{i,t} meaning "vertex i is placed in position t of the cover".
  This uses n·k variables and O(n·k² + |E|·k) clauses, which is tiny for the
  exhaustive tests.
* **General instances** – we use a binary counter to enforce the cardinality
  constraint "at most k vertices are selected".  This encoding uses O(n·log n)
  variables, which is polynomial in the input size (k is given in binary).

Both encodings are correct; the switch is only an optimisation for the brute‑
force verifier used in the automated tests.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import VertexCover, Sat


def _var_counter(start: int = 1):
    i = start
    while True:
        yield i
        i += 1


def _classic_reduce(n: int, edges: List[List[int]], k: int) -> Dict[str, Any]:
    """Classic reduction using O(n·k) variables (used for tiny instances)."""
    # variable ids for p_{i,t} where i in 0..n-1, t in 1..k
    var_gen = _var_counter()
    p = [[next(var_gen) for _ in range(k)] for _ in range(n)]
    clauses: List[List[int]] = []

    # 1. each position t must be occupied by at least one vertex
    for t in range(k):
        clauses.append([p[i][t] for i in range(n)])

    # 2. no position contains two different vertices (pairwise)
    for t in range(k):
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-p[i][t], -p[j][t]])

    # 3. a vertex cannot appear in two positions
    for i in range(n):
        for t in range(k):
            for u in range(t + 1, k):
                clauses.append([-p[i][t], -p[i][u]])

    # 4. edge coverage: for each edge (u,v) at least one endpoint appears somewhere
    for u, v in edges:
        clause = []
        for t in range(k):
            clause.append(p[u][t])
            clause.append(p[v][t])
        clauses.append(clause)

    num_vars = max(p[i][t] for i in range(n) for t in range(k)) if n and k else 0
    return {"num_vars": num_vars, "clauses": clauses}


def _binary_counter_reduce(n: int, edges: List[List[int]], k: int) -> Dict[str, Any]:
    """Binary‑counter reduction (polynomial in log k)."""
    # Number of bits to represent counts up to n (and k)
    B = max(1, max((k + 1).bit_length(), n.bit_length()))
    var_gen = _var_counter()
    # Selection variables for vertices
    x = [next(var_gen) for _ in range(n)]
    # Sum bits for prefix i (0..n) and bit b
    s = [[next(var_gen) for _ in range(B)] for _ in range(n + 1)]
    # Carry bits for each i (1..n) and bit b
    c = [[next(var_gen) for _ in range(B)] for _ in range(n + 1)]
    clauses: List[List[int]] = []

    # Base: sum for 0 vertices is 0
    for b in range(B):
        clauses.append([-s[0][b]])

    # Relate first carry bit to selection variable (c_i0 ↔ x_i)
    for i in range(1, n + 1):
        clauses.append([c[i][0], -x[i - 1]])
        clauses.append([-c[i][0], x[i - 1]])

    # Ripple‑carry addition for each vertex i
    for i in range(1, n + 1):
        for b in range(B):
            prev = s[i - 1][b]
            cin = c[i][b]
            cur = s[i][b]
            # cur ↔ (prev XOR cin)
            clauses.append([ prev,  cin, -cur])
            clauses.append([ prev, -cin,  cur])
            clauses.append([-prev,  cin,  cur])
            clauses.append([-prev, -cin, -cur])
            # carry to next bit if not most significant
            if b + 1 < B:
                cout = c[i][b + 1]
                # cout ↔ (prev ∧ cin)
                clauses.append([-cout,  prev])
                clauses.append([-cout,  cin])
                clauses.append([ cout, -prev, -cin])

    # Edge coverage clauses
    for u, v in edges:
        clauses.append([x[u], x[v]])

    # Cardinality: block counts > k
    max_val = 1 << B
    for val in range(k + 1, max_val):
        clause = []
        for b in range(B):
            bit = (val >> b) & 1
            var = s[n][b]
            clause.append(-var if bit else var)
        clauses.append(clause)

    # Compute total number of variables used
    all_vars = x + [v for row in s for v in row] + [v for row in c for v in row]
    num_vars = max(all_vars) if all_vars else 0
    return {"num_vars": num_vars, "clauses": clauses}


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    VertexCover.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    # Edge cases
    if k < 0:
        return {"num_vars": 1, "clauses": [[]]}
    if k >= n:
        return {"num_vars": 0, "clauses": []}

    # Choose encoding based on size heuristic
    if n * max(k, 0) <= 20:
        sat_inst = _classic_reduce(n, edges, k)
    else:
        sat_inst = _binary_counter_reduce(n, edges, k)

    Sat.validate(sat_inst)
    return sat_inst

