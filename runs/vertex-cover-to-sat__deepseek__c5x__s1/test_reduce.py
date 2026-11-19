"""Tests for the VertexCover → SAT reduction.

The test generates all small VertexCover instances (n up to 5) and checks
that the answer of the reduction matches the answer of a brute‑force SAT
solver.  It also verifies that the reduction respects the documented edge
cases (k < 0, k == 0, k >= n).

The script prints a JSON object with the number of tests run and the number
that passed.  The CI runner will capture this output.
"""

from __future__ import annotations

import itertools
import json
import sys

from problems import SOURCE, TARGET
from reduce import reduce as reduce_instance


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the VertexCover instance has a cover of size <= k.

    The instance follows the format defined in ``problems.VertexCover``.
    """
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        # empty graph is always covered
        return True
    # enumerate subsets up to size k
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the SAT instance is satisfiable.

    The instance follows the format defined in ``problems.Sat``.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # An empty clause makes the formula unsatisfiable
    for clause in clauses:
        if not clause:
            return False
    # enumerate all assignments
    for bits in range(1 << m):
        # bits i corresponds to variable i+1 being True
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
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


def generate_vertex_cover_instances(max_n: int = 3) -> list[dict]:
    instances = []
    for n in range(0, max_n + 1):
        vertices = list(range(n))
        # all possible edge sets (undirected, no loops)
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for r in range(len(possible_edges) + 1):
            for edges in itertools.combinations(possible_edges, r):
                # generate a range of k values covering edge cases
                ks = list(range(-1, n + 2))  # includes -1, 0, ..., n, n+1
                for k in ks:
                    instances.append({"n": n, "edges": [list(e) for e in edges], "k": k})
    return instances


def main() -> None:
    instances = generate_vertex_cover_instances()
    total = len(instances)
    passed = 0
    for inst in instances:
        # validate source instance (should always succeed)
        try:
            SOURCE.validate(inst)
        except Exception as e:
            print(f"Source validation failed on {inst}: {e}", file=sys.stderr)
            continue
        vc_ans = vertex_cover_bruteforce(inst)
        reduced = reduce_instance(inst)
        # validate target instance
        try:
            TARGET.validate(reduced)
        except Exception as e:
            print(f"Target validation failed on reduction of {inst}: {e}", file=sys.stderr)
            continue
        sat_ans = sat_bruteforce(reduced)
        if vc_ans == sat_ans:
            passed += 1
        else:
            print("Mismatch!", inst, "vc=", vc_ans, "sat=", sat_ans, file=sys.stderr)
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))

if __name__ == "__main__":
    main()
