"""Automated tests for the Clique → SAT reduction.

The script generates all small instances of the Clique problem (up to 5
vertices) and checks that the SAT instance produced by ``reduce`` has the same
answer as a brute‑force solver for Clique.

It also verifies that the reduction returns a syntactically valid SAT
instance (by calling ``Sat.validate``) and that the number of variables and
clauses are non‑negative integers as required.

The results are written to ``verdict.json`` in the repository root.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from problems import Clique, Sat
from reduce import reduce


def solve_clique_bruteforce(instance: dict) -> bool:
    n = instance["n"]
    edges = {frozenset((u, v)) for u, v in instance["edges"]}
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = list(range(n))
    for s in range(k, n + 1):
        for subset in itertools.combinations(vertices, s):
            if all(frozenset((a, b)) in edges for a, b in itertools.combinations(subset, 2)):
                return True
    return False


def solve_sat_bruteforce(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    if any(len(c) == 0 for c in clauses):
        return False
    if not clauses:
        return True
    for bits in range(1 << m):
        assignment = {i + 1: bool(bits & (1 << i)) for i in range(m)}
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = assignment.get(var, False)
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


def generate_all_clique_instances(max_n: int = 5) -> list[dict]:
    instances: list[dict] = []
    for n in range(max_n + 1):
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        for edge_mask in range(1 << len(pairs)):
            edges = []
            for idx, (u, v) in enumerate(pairs):
                if edge_mask & (1 << idx):
                    edges.append([u, v])
            for k in range(-1, n + 2):
                instances.append({"n": n, "edges": edges, "k": k})
    return instances


def main() -> None:
    # Restrict to instances where the SAT formula will be small enough for brute‑force.
    all_instances = [inst for inst in generate_all_clique_instances(max_n=5)
                     if inst["n"] * max(0, inst["k"]) <= 12]
    total = len(all_instances)
    passed = 0
    for idx, inst in enumerate(all_instances, 1):
        try:
            Clique.validate(inst)
        except Exception as e:
            print(f"Invalid generated instance #{idx}: {e}", file=sys.stderr)
            continue
        expected = solve_clique_bruteforce(inst)
        sat_inst = reduce(inst)
        try:
            Sat.validate(sat_inst)
        except Exception as e:
            print(f"Reduction produced invalid SAT instance for source #{idx}: {e}", file=sys.stderr)
            continue
        got = solve_sat_bruteforce(sat_inst)
        if expected == got:
            passed += 1
        else:
            print(f"Mismatch on instance #{idx}: expected {expected}, got {got}")
            print(inst)
            print(sat_inst)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()

