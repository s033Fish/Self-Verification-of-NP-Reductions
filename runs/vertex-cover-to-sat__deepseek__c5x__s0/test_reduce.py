"""Automated tests for the VertexCover → SAT reduction.

The script enumerates all small instances of VertexCover, solves them by
brute‑force, applies ``reduce`` and solves the resulting SAT instance by
brute‑force as well.  It then checks that the answers agree.

The result is written to ``verdict.json`` in the required format.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Tuple

import problems  # noqa: E402
from reduce import reduce  # noqa: E402


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the VertexCover instance is a YES instance.

    The definition follows the docstring in ``problems.VertexCover``.
    """
    n = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k = instance["k"]

    # Edge cases directly from the problem statement.
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True

    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            cover = set(subset)
            if all(u in cover or v in cover for u, v in edges):
                return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    """Return True iff the SAT instance is satisfiable.

    Implements the standard semantics from ``problems.Sat``.
    """
    m = instance["num_vars"]
    clauses = instance["clauses"]

    for clause in clauses:
        if not clause:
            return False

    for bits in itertools.product([False, True], repeat=m):
        assignment = {i + 1: bits[i] for i in range(m)}
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_all_instances(max_n: int = 4) -> List[dict]:
    """Generate all VertexCover instances with ``n <= max_n``.

    For each ``n`` we iterate over every possible edge subset and over a
    range of ``k`` values covering the interesting edge cases.
    """
    instances: List[dict] = []
    for n in range(max_n + 1):
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for edge_mask in range(1 << len(possible_edges)):
            edges = [list(possible_edges[i]) for i in range(len(possible_edges)) if (edge_mask >> i) & 1]
            ks = set([-1, 0, n // 2, n - 1, n, n + 1])
            for k in ks:
                instance = {"n": n, "edges": edges, "k": k}
                try:
                    problems.VertexCover.validate(instance)
                except Exception as e:
                    raise RuntimeError(f"Invalid generated instance: {instance}") from e
                instances.append(instance)
    return instances


def main() -> None:
    instances = generate_all_instances(max_n=4)
    total = len(instances)
    passed = 0
    for inst in instances:
        vc_answer = vertex_cover_bruteforce(inst)
        sat_inst = reduce(inst)
        problems.Sat.validate(sat_inst)
        sat_answer = sat_bruteforce(sat_inst)
        if vc_answer == sat_answer:
            passed += 1
        else:
            print("Mismatch found!", file=sys.stderr)
            print("VertexCover instance:", inst, file=sys.stderr)
            print("Expected (VC):", vc_answer, file=sys.stderr)
            print("Reduced SAT instance:", sat_inst, file=sys.stderr)
            print("SAT answer:", sat_answer, file=sys.stderr)
            break
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

