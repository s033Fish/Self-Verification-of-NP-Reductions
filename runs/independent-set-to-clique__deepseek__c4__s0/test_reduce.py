"""Tests: compare brute-force SOURCE answers with brute-force TARGET answers
on the reductions of many small instances, plus edge cases."""

from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce
from solvers import solve_clique, solve_independent_set


def all_graphs(n: int):
    """Yield every simple graph on n vertices as a list of edges."""
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        yield [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]


def check(instance: dict) -> None:
    SOURCE.validate(instance)
    out = reduce(instance)
    TARGET.validate(out)
    got = solve_clique(out)
    want = solve_independent_set(instance)
    assert got == want, (instance, out, want, got)


tests_run = 0
tests_passed = 0


def run(instance: dict) -> None:
    global tests_run, tests_passed
    tests_run += 1
    check(instance)
    tests_passed += 1


# Exhaustive over all graphs with n = 0..4 and a range of k values.
for n in range(0, 5):
    for edges in all_graphs(n):
        for k in range(-2, n + 3):
            run({"n": n, "edges": edges, "k": k})

# Random larger instances.
rng = random.Random(12345)
for _ in range(3000):
    n = rng.randint(0, 9)
    edges = []
    for u, v in itertools.combinations(range(n), 2):
        if rng.random() < 0.5:
            edges.append([u, v])
    k = rng.randint(-3, n + 3)
    run({"n": n, "edges": edges, "k": k})

# Specific edge cases.
run({"n": 0, "edges": [], "k": 0})
run({"n": 0, "edges": [], "k": 1})
run({"n": 5, "edges": [], "k": 5})
run({"n": 5, "edges": [], "k": 6})
run({"n": 5, "edges": [], "k": -1})
complete = [[u, v] for u, v in itertools.combinations(range(5), 2)]
run({"n": 5, "edges": complete, "k": 1})
run({"n": 5, "edges": complete, "k": 2})
run({"n": 5, "edges": complete, "k": 0})
# reversed / shuffled edge orientation should not matter
run({"n": 4, "edges": [[1, 0], [3, 2]], "k": 2})

# Verify reduction output shape on a sample.
sample = {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}
out = reduce(sample)
assert out == {"n": 4, "edges": [[0, 2], [0, 3], [1, 2], [1, 3]], "k": 2}, out
tests_run += 1
tests_passed += 1

print(f"tests_run={tests_run} tests_passed={tests_passed}")
assert tests_run == tests_passed
