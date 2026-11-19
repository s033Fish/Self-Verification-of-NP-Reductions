"""Independent verification of reduce.py (VertexCover -> IndependentSet).

We implement brute-force solvers for both problems directly from the
docstrings in problems.py, then compare answers on many small source
instances and their reductions.
"""

from __future__ import annotations

import itertools
import time

from problems import VertexCover, IndependentSet
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.
# ----------------------------------------------------------------------


def vertex_cover_yes(instance) -> bool:
    """Yes iff there is a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def independent_set_yes(instance) -> bool:
    """Yes iff there is an independent set of AT LEAST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(not (u in chosen and v in chosen) for u, v in edges):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation
# ----------------------------------------------------------------------


def all_graphs(n):
    """All simple undirected graphs on n vertices, as edge lists."""
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        yield [[u, v] for i, (u, v) in enumerate(possible) if mask >> i & 1]


def source_instances():
    """Many small VertexCover instances, including edge cases."""
    for n in range(0, 6):
        for edges in all_graphs(n):
            # k from negative through beyond n, to hit all edge cases.
            for k in range(-2, n + 3):
                yield {"n": n, "edges": edges, "k": k}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in source_instances():
        tests_run += 1
        # Both instances must be valid for their respective problems.
        VertexCover.validate(inst)
        reduced = reduce(inst)
        IndependentSet.validate(reduced)

        src_ans = vertex_cover_yes(inst)
        tgt_ans = independent_set_yes(reduced)

        if src_ans == tgt_ans:
            tests_passed += 1
        else:
            failures.append((inst, reduced, src_ans, tgt_ans))

    # Also verify reduce does not mutate the input.
    sample = {"n": 4, "edges": [[0, 1], [1, 2]], "k": 1}
    import copy
    before = copy.deepcopy(sample)
    reduce(sample)
    if sample != before:
        failures.append(("mutated input", sample, before, None, None))
    tests_run += 1
    if sample == before:
        tests_passed += 1

    # Verify reduce is fast (polynomial) on a large instance: no brute force.
    n_big = 2000
    edges_big = [[i, i + 1] for i in range(n_big - 1)]
    big = {"n": n_big, "edges": edges_big, "k": n_big // 2}
    start = time.time()
    out_big = reduce(big)
    elapsed = time.time() - start
    tests_run += 1
    if out_big == {"n": n_big, "edges": edges_big, "k": n_big - n_big // 2} and elapsed < 2.0:
        tests_passed += 1
    else:
        failures.append(("large instance", elapsed, out_big["k"], None, None))

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print(f)
    else:
        print("All tests passed.")

    return tests_run, tests_passed, failures


if __name__ == "__main__":
    main()


def random_extra():
    """Randomized checks on somewhat larger graphs."""
    import random
    rng = random.Random(12345)
    run = passed = 0
    for _ in range(3000):
        n = rng.randint(0, 9)
        possible = list(itertools.combinations(range(n), 2))
        edges = [list(e) for e in possible if rng.random() < 0.4]
        k = rng.randint(-2, n + 2)
        inst = {"n": n, "edges": edges, "k": k}
        reduced = reduce(inst)
        run += 1
        if vertex_cover_yes(inst) == independent_set_yes(reduced):
            passed += 1
    return run, passed
