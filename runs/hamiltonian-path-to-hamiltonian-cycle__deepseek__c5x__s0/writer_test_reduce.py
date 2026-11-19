"""Exhaustive tests: compare brute-force answers on source instances and
their reductions, for all graphs up to n = 5 (plus edge cases)."""

from __future__ import annotations

from itertools import combinations

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import hamiltonian_cycle, hamiltonian_path

tests_run = 0
tests_passed = 0


def check(n, edges):
    global tests_run, tests_passed
    instance = {"n": n, "edges": [list(e) for e in edges]}
    SOURCE.validate(instance)
    out = reduce(instance)
    TARGET.validate(out)
    src = hamiltonian_path(n, instance["edges"])
    tgt = hamiltonian_cycle(out["n"], out["edges"])
    tests_run += 1
    if src == tgt:
        tests_passed += 1
        return True
    print(f"FAIL n={n} edges={instance['edges']} src={src} tgt={tgt} out={out}")
    return False


def all_graphs(n):
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [pairs[i] for i in range(len(pairs)) if mask >> i & 1]


ok = True

# Exhaustive over all simple graphs for n = 0..5.
for n in range(0, 6):
    for edges in all_graphs(n):
        ok &= check(n, edges)

# A few larger random-ish structured cases.
check(6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]])          # path, yes
check(6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0]])    # cycle, yes
check(6, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [0, 5]])    # cycle, yes
check(7, [[i, j] for i in range(7) for j in range(i + 1, 7)])  # complete, yes
check(6, [])                                                   # empty, no

print(f"tests_run={tests_run} tests_passed={tests_passed} ok={ok and tests_run == tests_passed}")
