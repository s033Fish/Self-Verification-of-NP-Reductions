"""Independent tests for reduce.py: VertexCover -> SetCover.

We implement brute-force solvers for both problems directly from the
docstrings in problems.py, then compare answers on many small instances.
"""
from __future__ import annotations

import itertools
import random

from problems import VertexCover, SetCover
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers
# ----------------------------------------------------------------------

def solve_vertex_cover(instance) -> bool:
    """Yes iff graph has a vertex cover of AT MOST k vertices."""
    VertexCover.validate(instance)
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True  # empty set covers; k >= 0 here
    # Try every subset of vertices of size <= k.
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return True
    return False


def solve_set_cover(instance) -> bool:
    """Yes iff AT MOST k of the sets together contain every element."""
    SetCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]
    if k < 0:
        return False
    if u == 0:
        return True  # empty universe, k >= 0
    # If some element is in no set -> no.
    union_all = set()
    for s in sets:
        union_all.update(s)
    if union_all != set(range(u)):
        return False
    for size in range(0, min(k, len(sets)) + 1):
        for combo in itertools.combinations(range(len(sets)), size):
            covered = set()
            for i in combo:
                covered.update(sets[i])
            if len(covered) == u:
                return True
    return False


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def random_vc_instance(rng, max_n=6, max_edges=8):
    n = rng.randint(0, max_n)
    all_edges = list(itertools.combinations(range(n), 2))
    rng.shuffle(all_edges)
    m = rng.randint(0, min(max_edges, len(all_edges)))
    edges = [list(e) for e in all_edges[:m]]
    k = rng.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def exhaustive_vc_instances():
    """All graphs on n<=4 vertices (all edge subsets) with k in -1..n+1."""
    for n in range(0, 5):
        all_edges = list(itertools.combinations(range(n), 2))
        for r in range(len(all_edges) + 1):
            for edge_subset in itertools.combinations(all_edges, r):
                edges = [list(e) for e in edge_subset]
                for k in range(-1, n + 2):
                    yield {"n": n, "edges": edges, "k": k}


# ----------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------

def check_instance(inst, results):
    results["run"] += 1
    src = solve_vertex_cover(inst)
    target = reduce(inst)
    # reduction output must itself be a valid SetCover instance
    SetCover.validate(target)
    tgt = solve_set_cover(target)
    if src == tgt:
        results["passed"] += 1
    else:
        results["failures"].append((inst, target, src, tgt))


def test_exhaustive():
    results = {"run": 0, "passed": 0, "failures": []}
    for inst in exhaustive_vc_instances():
        check_instance(inst, results)
    return results


def test_random(seed=12345, count=3000):
    rng = random.Random(seed)
    results = {"run": 0, "passed": 0, "failures": []}
    for _ in range(count):
        inst = random_vc_instance(rng)
        check_instance(inst, results)
    return results


def test_edge_cases():
    results = {"run": 0, "passed": 0, "failures": []}
    cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": -1},
        {"n": 0, "edges": [], "k": 5},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": -1},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [[0, 1]], "k": 0},
        {"n": 3, "edges": [[0, 1]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [2, 3]], "k": -1},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 3},
        {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]], "k": 2},
        # k >= n always yes
        {"n": 2, "edges": [[0, 1]], "k": 2},
        {"n": 2, "edges": [[0, 1]], "k": 100},
    ]
    for inst in cases:
        check_instance(inst, results)
    return results


def test_reduction_structure():
    """Sanity checks on the reduction output shape."""
    results = {"run": 0, "passed": 0, "failures": []}
    inst = {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2}
    target = reduce(inst)
    results["run"] += 1
    ok = (
        target["universe_size"] == 3
        and target["k"] == 2
        and len(target["sets"]) == 4
        and target["sets"][0] == [0]
        and target["sets"][1] == [0, 1]
        and target["sets"][2] == [1, 2]
        and target["sets"][3] == [2]
    )
    if ok:
        results["passed"] += 1
    else:
        results["failures"].append(("structure", target))
    return results


def main():
    all_results = []
    for name, fn in [
        ("exhaustive", test_exhaustive),
        ("random", test_random),
        ("edge_cases", test_edge_cases),
        ("structure", test_reduction_structure),
    ]:
        res = fn()
        all_results.append((name, res))
        print(f"{name}: run={res['run']} passed={res['passed']} failures={len(res['failures'])}")
        for f in res["failures"][:5]:
            print("   FAIL:", f)

    total_run = sum(r["run"] for _, r in all_results)
    total_passed = sum(r["passed"] for _, r in all_results)
    print(f"TOTAL: run={total_run} passed={total_passed}")
    return total_run, total_passed


if __name__ == "__main__":
    main()
