"""Test the reduction from DominatingSet to SAT.

The script brute‑forces both the source and target problems for all small
instances (n ≤ 4) and checks that ``reduce`` produces a SAT instance whose
answer matches the original Dominating‑Set answer.

It records the number of tests run and the number that passed, then writes
``verdict.json`` in the repository root.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict, Any

from problems import DominatingSet, Sat
from reduce import reduce


def dominating_set_bruteforce(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges: List[List[int]] = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if n == 0:
        return k >= 0
    if k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    vertices = list(range(n))
    for r in range(k + 1):
        for combo in itertools.combinations(vertices, r):
            dom_set = set(combo)
            ok = True
            for v in range(n):
                if v in dom_set:
                    continue
                if not (adj[v] & dom_set):
                    ok = False
                    break
            if ok:
                return True
    return False


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for clause in clauses:
        if len(clause) == 0:
            return False
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
                if lit > 0 and val == 1:
                    clause_ok = True
                    break
                if lit < 0 and val == 0:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def generate_all_graphs(n: int) -> List[List[List[int]]]:
    vertices = list(range(n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    all_graphs: List[List[List[int]]] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[List[int]] = []
        for i, (u, v) in enumerate(possible_edges):
            if (mask >> i) & 1:
                edges.append([u, v])
        all_graphs.append(edges)
    return all_graphs


def main() -> None:
    total = 0
    passed = 0
    # n up to 4 to keep SAT brute‑force tractable
    for n in range(0, 5):
        all_edges = generate_all_graphs(n)
        for edges in all_edges:
            for k in range(-1, n + 2):
                instance = {"n": n, "edges": edges, "k": k}
                DominatingSet.validate(instance)
                src_ans = dominating_set_bruteforce(instance)
                target = reduce(instance)
                Sat.validate(target)
                tgt_ans = sat_bruteforce(target)
                total += 1
                if src_ans == tgt_ans:
                    passed += 1
                else:
                    print("Mismatch!", instance, "=>", src_ans, tgt_ans, file=sys.stderr)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
