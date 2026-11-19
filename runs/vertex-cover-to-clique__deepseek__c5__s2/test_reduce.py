"""Independent brute-force verification of reduce.py (Vertex Cover -> Clique).

We implement our own solvers directly from the problem definitions, generate
many small source instances, reduce them, and compare answers.
"""

from __future__ import annotations

import itertools

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers written from the definitions in problems.py
# ----------------------------------------------------------------------

def vertex_cover_yes(instance: dict) -> bool:
    """Yes iff some vertex set of size <= k covers every edge."""
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def clique_yes(instance: dict) -> bool:
    """Yes iff some vertex set of size >= k is a clique."""
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            if all(frozenset((u, v)) in edges
                   for u, v in itertools.combinations(subset, 2)):
                return True
    return False


# ----------------------------------------------------------------------
# Instance generation: every graph on n <= 5 vertices, many k values
# ----------------------------------------------------------------------

def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield edges


def source_instances():
    for n in range(0, 6):
        for edges in all_graphs(n):
            for k in range(-2, n + 3):
                yield {"n": n, "edges": [list(e) for e in edges], "k": k}


def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    for inst in source_instances():
        tests_run += 1
        # Input must be a valid source instance.
        SOURCE.validate(inst)
        expected = vertex_cover_yes(inst)

        # Reduction must produce a valid target instance.
        out = reduce(inst)
        TARGET.validate(out)

        # k must be an int, n preserved; sanity on structure.
        assert isinstance(out["k"], int)
        assert out["n"] == inst["n"]

        got = clique_yes(out)
        if got == expected:
            tests_passed += 1
        else:
            failures.append((inst, out, expected, got))

    print(f"tests_run={tests_run} tests_passed={tests_passed} "
          f"failures={len(failures)}")
    for f in failures[:10]:
        print("FAIL:", f)

    # A few hand-picked edge cases explicitly.
    edge_cases = [
        ({"n": 0, "edges": [], "k": -1}, False),
        ({"n": 0, "edges": [], "k": 0}, True),
        ({"n": 3, "edges": [], "k": 0}, True),
        ({"n": 3, "edges": [], "k": -1}, False),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}, False),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}, True),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 3}, True),
        ({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}, True),
        ({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1}, False),
        ({"n": 1, "edges": [], "k": 0}, True),
        ({"n": 1, "edges": [], "k": -5}, False),
    ]
    for inst, expected in edge_cases:
        tests_run += 1
        SOURCE.validate(inst)
        out = reduce(inst)
        TARGET.validate(out)
        if clique_yes(out) == expected:
            tests_passed += 1
        else:
            failures.append((inst, out, expected, clique_yes(out)))
            print("EDGE FAIL:", inst, out, expected)

    print(f"FINAL tests_run={tests_run} tests_passed={tests_passed}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
