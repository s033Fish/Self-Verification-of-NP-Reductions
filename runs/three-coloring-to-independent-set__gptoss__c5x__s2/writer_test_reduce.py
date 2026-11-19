import random
import itertools
import json
from typing import List, Dict, Any

from problems import ThreeColoring, IndependentSet, InvalidInstance
from reduce import reduce


def three_coloring_bruteforce(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    # Edge cases from definition
    if n == 0:
        return True
    if n <= 3:
        return True
    # Check for K4 (4 mutually adjacent vertices) quickly
    # but brute-force will handle anyway
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def independent_set_bruteforce(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # iterate subsets of size >= k
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def random_graph(max_n: int = 5, edge_prob: float = 0.4) -> Dict[str, Any]:
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def run_tests(num_tests: int = 200) -> Dict[str, int]:
    passed = 0
    for _ in range(num_tests):
        src = random_graph()
        # validate source
        try:
            ThreeColoring.validate(src)
        except InvalidInstance as e:
            # Should not happen
            raise AssertionError(f"Invalid source instance generated: {e}")
        # compute answers
        ans_src = three_coloring_bruteforce(src)
        red = reduce(src)
        # validate target
        IndependentSet.validate(red)
        ans_tgt = independent_set_bruteforce(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", src, red, ans_src, ans_tgt)
            break
    return {"tests_run": num_tests, "tests_passed": passed}

if __name__ == "__main__":
    result = run_tests(200)
    result["verified"] = result["tests_passed"] == result["tests_run"]
    with open("verdict.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
