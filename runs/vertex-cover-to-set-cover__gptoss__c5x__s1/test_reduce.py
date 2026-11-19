"""Independent tests for reduce.py: Vertex Cover -> Set Cover.

We implement our own brute-force solvers from the definitions in problems.py
(which provides no solvers) and compare answers on many small instances.
"""

from __future__ import annotations

import itertools
import random

from problems import VertexCover, SetCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers (written from the problem definitions)

def vertex_cover_answer(instance) -> bool:
    """True iff graph has a vertex cover of size AT MOST k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers no edges, k >= 0
    max_size = min(k, n)
    for size in range(0, max_size + 1):
        for chosen in itertools.combinations(range(n), size):
            chosen = set(chosen)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def set_cover_answer(instance) -> bool:
    """True iff AT MOST k of the sets cover the whole universe."""
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]
    if k < 0:
        return False
    if u == 0:
        return True  # empty universe covered by no sets, k >= 0
    max_size = min(k, len(sets))
    for size in range(0, max_size + 1):
        for chosen in itertools.combinations(range(len(sets)), size):
            covered = set()
            for i in chosen:
                covered.update(sets[i])
            if len(covered) == u:
                return True
    return False


# ----------------------------------------------------------------------
# Instance enumeration

def all_graphs(n):
    """All simple graphs on n labelled vertices (as edge lists)."""
    possible = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if mask & (1 << i)]
        yield edges


def exhaustive_instances():
    for n in range(0, 5):
        for edges in all_graphs(n):
            for k in range(-1, n + 2):
                yield {"n": n, "edges": edges, "k": k}


def random_instances(count=2000, seed=12345):
    rng = random.Random(seed)
    for _ in range(count):
        n = rng.randint(0, 6)
        possible = list(itertools.combinations(range(n), 2))
        edges = [list(e) for e in possible if rng.random() < 0.5]
        k = rng.randint(-2, n + 2)
        yield {"n": n, "edges": edges, "k": k}


# ----------------------------------------------------------------------
# Tests

def run():
    tests_run = 0
    tests_passed = 0
    failures = []

    instances = list(exhaustive_instances()) + list(random_instances())

    for inst in instances:
        tests_run += 1
        # source must be valid
        VertexCover.validate(inst)
        expected = vertex_cover_answer(inst)
        try:
            target = reduce(inst)
            SetCover.validate(target)
            got = set_cover_answer(target)
        except Exception as exc:  # reduction crashed
            failures.append((inst, "exception: %r" % (exc,)))
            continue
        if got == expected:
            tests_passed += 1
        else:
            failures.append((inst, expected, got))

    # Additional targeted edge cases
    targeted = [
        {"n": 0, "edges": [], "k": 0},          # empty graph, empty cover
        {"n": 0, "edges": [], "k": -1},         # k < 0 -> no
        {"n": 3, "edges": [], "k": 0},          # no edges -> yes
        {"n": 3, "edges": [], "k": -1},         # no edges but k<0 -> no
        {"n": 3, "edges": [[0, 1]], "k": 0},    # need one vertex
        {"n": 3, "edges": [[0, 1]], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 2, "edges": [[0, 1]], "k": 5},    # k >= n -> yes
    ]
    for inst in targeted:
        tests_run += 1
        VertexCover.validate(inst)
        expected = vertex_cover_answer(inst)
        try:
            target = reduce(inst)
            SetCover.validate(target)
            got = set_cover_answer(target)
        except Exception as exc:
            failures.append((inst, "exception: %r" % (exc,)))
            continue
        if got == expected:
            tests_passed += 1
        else:
            failures.append((inst, expected, got))

    print("tests_run=%d tests_passed=%d" % (tests_run, tests_passed))
    if failures:
        print("FAILURES (%d):" % len(failures))
        for f in failures[:20]:
            print("  ", f)
    return tests_run, tests_passed, failures


if __name__ == "__main__":
    run()
