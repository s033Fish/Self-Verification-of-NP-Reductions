"""Tests for the Clique → SAT reduction.

We implement brute‑force solvers for Clique and SAT and compare answers on a
set of generated instances.  To keep the runtime reasonable we limit the
exhaustive enumeration to n ≤ 3 (so at most 9 SAT variables) and use a modest
number of random instances.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from pathlib import Path

from problems import Clique, Sat
from reduce import reduce as reduce_instance


def solve_clique(inst: dict) -> bool:
    n = inst["n"]
    edges = {frozenset(e) for e in inst["edges"]}
    k = inst["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    verts = list(range(n))
    for size in range(k, n + 1):
        for subset in itertools.combinations(verts, size):
            if all(frozenset((u, v)) in edges for u, v in itertools.combinations(subset, 2)):
                return True
    return False


def solve_sat(inst: dict) -> bool:
    m = inst["num_vars"]
    clauses = inst["clauses"]
    if any(len(c) == 0 for c in clauses):
        return False
    if not clauses:
        return True
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((lit > 0 and bits[abs(lit) - 1]) or (lit < 0 and not bits[abs(lit) - 1]) for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def exhaustive_instances(max_n: int = 3) -> list[dict]:
    instances = []
    for n in range(max_n + 1):
        verts = list(range(n))
        all_edges = list(itertools.combinations(verts, 2))
        for mask in range(1 << len(all_edges)):
            edges = []
            for i, (u, v) in enumerate(all_edges):
                if (mask >> i) & 1:
                    edges.append([u, v])
            for k in range(-1, n + 2):
                instances.append({"n": n, "edges": edges, "k": k})
    return instances


def random_instances(num: int = 30, max_n: int = 5) -> list[dict]:
    rnd = random.Random(0)
    out = []
    for _ in range(num):
        n = rnd.randint(0, max_n)
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if rnd.random() < 0.5:
                    edges.append([u, v])
        k = rnd.randint(-2, n + 2)
        out.append({"n": n, "edges": edges, "k": k})
    return out


def main() -> None:
    instances = exhaustive_instances(3) + random_instances(30, 5)
    total = len(instances)
    passed = 0
    for idx, inst in enumerate(instances, 1):
        Clique.validate(inst)
        sat_inst = reduce_instance(inst)
        Sat.validate(sat_inst)
        if solve_clique(inst) != solve_sat(sat_inst):
            print(f"Mismatch on {idx}/{total}: {inst}\nSAT:{sat_inst}\n", file=sys.stderr)
            sys.exit(1)
        passed += 1
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
