"""Tests for the Vertex Cover -> Dominating Set reduction."""
from __future__ import annotations

import itertools
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ------------------------- brute-force solvers -------------------------

def vertex_cover_answer(instance):
    """True iff the graph has a vertex cover of at most k vertices."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            chosen = set(combo)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def dominating_set_answer(instance):
    """True iff the graph has a dominating set of at most k vertices."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    for size in range(0, k + 1):
        for combo in itertools.combinations(range(n), size):
            dom = set(combo)
            for v in combo:
                dom |= adj[v]
            if len(dom) == n:
                return True
    return False


# ------------------------- instance generation -------------------------

def random_instance(rng, max_n=6, max_k=6):
    n = rng.randint(0, max_n)
    all_pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(all_pairs)
    m = rng.randint(0, len(all_pairs))
    edges = [list(e) for e in all_pairs[:m]]
    rng.shuffle(edges)
    k = rng.randint(-2, max_k)
    return {"n": n, "edges": edges, "k": k}


def all_small_instances():
    """Exhaustive over n <= 4, all edge subsets, all k in -1..n+1."""
    for n in range(0, 5):
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for mask in range(1 << len(pairs)):
            edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
            for k in range(-1, n + 2):
                yield {"n": n, "edges": [list(e) for e in edges], "k": k}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(inst, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        SOURCE.validate(inst)
        out = reduce(inst)
        TARGET.validate(out)
        expected = vertex_cover_answer(inst)
        got = dominating_set_answer(out)
        if expected == got:
            tests_passed += 1
        else:
            failures.append((label, inst, out, expected, got))

    # exhaustive small instances
    for inst in all_small_instances():
        check(inst, "exhaustive")

    # random instances
    rng = random.Random(12345)
    for _ in range(4000):
        check(random_instance(rng), "random")

    # explicit edge cases
    explicit = [
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 1, "edges": [], "k": -1},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 1},
        {"n": 4, "edges": [], "k": 0},
        {"n": 4, "edges": [], "k": 3},
        {"n": 2, "edges": [[0, 1]], "k": 0},
        {"n": 2, "edges": [[0, 1]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2]], "k": 0},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 3},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2},
    ]
    for inst in explicit:
        check(inst, "explicit")

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:10]:
        print("FAIL", f)

    import json
    verdict = {
        "verified": len(failures) == 0 and tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)
    return 0 if verdict["verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
