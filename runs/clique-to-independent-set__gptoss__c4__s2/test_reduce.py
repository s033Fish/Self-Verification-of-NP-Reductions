import random
import itertools
import json
from problems import Clique, IndependentSet
from reduce import reduce


def brute_clique(instance):
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
    # check all subsets of size >= k
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def brute_independent(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # empty graph case handled by general loop
    for size in range(k, n + 1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def random_instance(n, edge_prob=0.5, k_range=(-1, None)):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    if k_range[1] is None:
        max_k = n
    else:
        max_k = k_range[1]
    k = random.randint(k_range[0], max_k)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        n = random.randint(0, 6)  # small for brute force
        inst = random_instance(n, edge_prob=0.5, k_range=(-2, n+2))
        # validate instances (may raise)
        Clique.validate(inst)
        # reduce
        red = reduce(inst)
        IndependentSet.validate(red)
        # compare answers
        ans1 = brute_clique(inst)
        ans2 = brute_independent(red)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch!", inst, red, ans1, ans2)
            break
    return passed, num_trials

if __name__ == "__main__":
    passed, total = run_tests(500)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
