"""Test the correctness of the Hamiltonian Cycle → SAT reduction.

The test suite performs a brute‑force check on all small graphs (up to 4
vertices). For each graph we compute the answer to the Hamiltonian Cycle
problem using an exhaustive permutation search and compare it with the
answer to the SAT instance produced by ``reduce`` using a brute‑force SAT
solver. The reduction is considered correct if the two answers coincide
for every tested instance.

The script records the total number of tests run and how many passed and
writes a ``verdict.json`` file as required by the task description.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from problems import HamiltonianCycle, Sat
from reduce import reduce as reduce_instance


def hamiltonian_cycle_bruteforce(instance: dict) -> bool:
    n = instance["n"]
    if n <= 2:
        return False
    edge_set = {frozenset(e) for e in instance["edges"]}
    vertices = list(range(n))
    for perm in itertools.permutations(vertices[1:]):
        cycle = (0, *perm)
        ok = True
        for i in range(n):
            u = cycle[i]
            v = cycle[(i + 1) % n]
            if frozenset((u, v)) not in edge_set:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(instance: dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for clause in clauses:
        if not clause:
            return False
    for bits in range(1 << m):
        satisfied = True
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
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_all_graphs(max_n: int):
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if (mask >> i) & 1:
                    edges.append([u, v])
            yield {"n": n, "edges": edges}


def main() -> None:
    total = 0
    passed = 0
    for instance in generate_all_graphs(4):
        HamiltonianCycle.validate(instance)
        src_ans = hamiltonian_cycle_bruteforce(instance)
        target = reduce_instance(instance)
        Sat.validate(target)
        tgt_ans = sat_bruteforce(target)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", instance, file=sys.stderr)
            print("Source answer:", src_ans, file=sys.stderr)
            print("Target answer:", tgt_ans, file=sys.stderr)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()

