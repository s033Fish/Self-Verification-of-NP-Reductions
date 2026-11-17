import random
import itertools
import json
import sys
from typing import List, Dict, Any

import problems
from reduce import reduce


def solve_clique(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    # edge cases
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # brute force search for clique of size >= k
    vertices = list(range(n))
    for size in range(k, n + 1):
        for combo in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(combo, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def solve_independent(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # brute force
    vertices = list(range(n))
    for size in range(k, n + 1):
        for combo in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(combo, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def random_instance(n_max=5, edge_prob=0.5):
    n = random.randint(0, n_max)
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    k = random.randint(-1, n + 2)  # include some out-of-range values
    return {"n": n, "edges": edges, "k": k}


def main():
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_instance()
        # validate source
        try:
            problems.Clique.validate(inst)
        except Exception as e:
            # skip invalid generated instances (should be valid)
            continue
        reduced = reduce(inst)
        # compare answers
        ans1 = solve_clique(inst)
        ans2 = solve_independent(reduced)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch!", inst, reduced, ans1, ans2)
            sys.exit(1)
    # also test some deterministic edge cases
    edge_cases = [
        {"n": 0, "edges": [], "k": -5},
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 3, "edges": [], "k": 2},
        {"n": 3, "edges": [[0,1],[1,2],[0,2]], "k": 3},
    ]
    for inst in edge_cases:
        problems.Clique.validate(inst)
        reduced = reduce(inst)
        assert solve_clique(inst) == solve_independent(reduced)
        passed += 1
    total = tests + len(edge_cases)
    print(f"All {passed}/{total} tests passed.")
    # write verdict
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
