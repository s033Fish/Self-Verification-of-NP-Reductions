"""Test suite for the Dominating Set → SAT reduction.

The repository provides only validation for instances.  This file implements
brute‑force solvers for both problems and checks that ``reduce`` produces a SAT
instance whose answer matches the original Dominating‑Set instance.

The tests enumerate all graphs with up to ``MAX_N`` vertices (including the
empty graph) and a range of ``k`` values.  For each graph we:

1. Compute the exact answer for Dominating Set using exhaustive search.
2. Apply ``reduce`` to obtain a SAT instance.
3. Compute the exact answer for the SAT instance using exhaustive search.
4. Verify that the two answers are identical.

If any mismatch is found the script exits with a non‑zero status so that the
verdict reflects a failed reduction.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

# Import the modules under test.
import problems  # noqa: F401 – needed for validation side‑effects
from reduce import reduce  # type: ignore

# ---------------------------------------------------------------------------
# Brute‑force solvers
# ---------------------------------------------------------------------------


def dominating_set_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has a dominating set of size at most ``k``.

    The instance follows the format defined in ``DominatingSet``.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if n == 0:
        return k >= 0
    if k >= n:
        return True

    # Build adjacency list.
    neighbours = [set() for _ in range(n)]
    for u, v in edges:
        neighbours[u].add(v)
        neighbours[v].add(u)

    vertices = list(range(n))
    for size in range(k + 1):
        for combo in itertools.combinations(vertices, size):
            dominated = set(combo)
            for v in combo:
                dominated.update(neighbours[v])
            if len(dominated) == n:
                return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the CNF formula is satisfiable.

    ``instance`` follows the format defined in ``Sat``.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    for clause in clauses:
        if not clause:
            return False

    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = bool((bits >> var) & 1)
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False

# ---------------------------------------------------------------------------
# Test generation and execution
# ---------------------------------------------------------------------------

# We limit ``MAX_N`` to 4 because the reduction introduces O(n*k) auxiliary
# variables.  For n=5 and k up to n the SAT instance can have up to 30 vars,
# making exhaustive SAT checking infeasible in the time limit of the review
# environment.  n=4 keeps the variable count ≤ 16, which is fast enough.
MAX_N = 4


def generate_all_graphs(n: int):
    """Yield all simple undirected graphs on ``n`` vertices.

    Each graph is represented as a list of edges ``[u, v]`` with ``u < v``.
    """
    vertices = list(range(n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    for mask in range(1 << len(possible_edges)):
        edges = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        yield edges


def main() -> None:
    total = 0
    passed = 0
    for n in range(MAX_N + 1):
        for edges in generate_all_graphs(n):
            for k in range(-1, n + 2):  # include edge cases
                instance = {"n": n, "edges": edges, "k": k}
                problems.DominatingSet.validate(instance)
                ds_ans = dominating_set_bruteforce(instance)
                sat_inst = reduce(instance)
                problems.Sat.validate(sat_inst)
                sat_ans = sat_bruteforce(sat_inst)
                total += 1
                if ds_ans == sat_ans:
                    passed += 1
                else:
                    sys.stderr.write(f"Mismatch n={n}, k={k}, edges={edges}\n")
                    sys.stderr.write(f"DominatingSet={ds_ans}, Sat={sat_ans}\n")
                    Path("verdict.json").write_text(
                        json.dumps({"verified": False, "tests_run": total, "tests_passed": passed}, indent=2)
                    )
                    sys.exit(1)
    Path("verdict.json").write_text(
        json.dumps({"verified": True, "tests_run": total, "tests_passed": passed}, indent=2)
    )

if __name__ == "__main__":
    main()

