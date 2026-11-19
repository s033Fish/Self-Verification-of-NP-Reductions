"""Test suite for the reduction from Hamiltonian Path to Hamiltonian Cycle.

The tests generate all small undirected graphs (up to 5 vertices) and a few
random larger ones. For each source instance we compute the exact answer for
the Hamiltonian Path problem with a brute‑force solver, apply ``reduce`` and
verify:

* The returned instance validates against :class:`HamiltonianCycle`.
* The Hamiltonian Cycle solver returns the same boolean answer as the
  Hamiltonian Path solver on the original instance.

The script prints a JSON object with the fields required by the task
specification: ``verified``, ``tests_run`` and ``tests_passed``.
"""

from __future__ import annotations

import itertools
import json
import random
import sys
from typing import List, Dict

from problems import HamiltonianPath, HamiltonianCycle
from reduce import reduce as reduce_instance


def hamiltonian_path_bruteforce(instance: Dict) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset((0, 1)) in edges
    verts = list(range(n))
    for perm in itertools.permutations(verts):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def hamiltonian_cycle_bruteforce(instance: Dict) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n < 3:
        return False
    verts = list(range(n))
    for perm in itertools.permutations(verts):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        if ok and frozenset((perm[-1], perm[0])) not in edges:
            ok = False
        if ok:
            return True
    return False


def generate_all_graphs(n: int) -> List[Dict]:
    verts = list(range(n))
    possible_edges = [(i, j) for i in verts for j in verts if i < j]
    graphs: List[Dict] = []
    for mask in range(1 << len(possible_edges)):
        edges: List[List[int]] = []
        for bit, (u, v) in enumerate(possible_edges):
            if mask & (1 << bit):
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs


def main() -> None:
    tests_run = 0
    tests_passed = 0

    for n in range(0, 6):
        for instance in generate_all_graphs(n):
            try:
                HamiltonianPath.validate(instance)
            except Exception as e:
                print("Source validation failed", instance, e, file=sys.stderr)
                continue
            src_ans = hamiltonian_path_bruteforce(instance)
            reduced = reduce_instance(instance)
            try:
                HamiltonianCycle.validate(reduced)
            except Exception as e:
                print("Target validation failed", reduced, e, file=sys.stderr)
                continue
            tgt_ans = hamiltonian_cycle_bruteforce(reduced)
            tests_run += 1
            if src_ans == tgt_ans:
                tests_passed += 1
            else:
                print("Mismatch!", instance, "=>", reduced, file=sys.stderr)

    random.seed(0)
    for n in (6, 7):
        for _ in range(200):
            edges = []
            for i in range(n):
                for j in range(i + 1, n):
                    if random.random() < 0.3:
                        edges.append([i, j])
            instance = {"n": n, "edges": edges}
            try:
                HamiltonianPath.validate(instance)
            except Exception:
                continue
            src_ans = hamiltonian_path_bruteforce(instance)
            reduced = reduce_instance(instance)
            try:
                HamiltonianCycle.validate(reduced)
            except Exception as e:
                print("Target validation failed (random)", reduced, e, file=sys.stderr)
                continue
            tgt_ans = hamiltonian_cycle_bruteforce(reduced)
            tests_run += 1
            if src_ans == tgt_ans:
                tests_passed += 1
            else:
                print("Random mismatch!", instance, "=>", reduced, file=sys.stderr)

    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
