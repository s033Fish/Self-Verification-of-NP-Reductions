import random
import itertools
import json
from problems import Clique, IndependentSet
from reduce import reduce


def brute_clique(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    if k <= 0:
        return True
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


def brute_independent_set(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
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


def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = []
    for u, v in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n + 2)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=2000):
    passed = 0
    for i in range(num):
        src = random_instance()
        # validate source
        Clique.validate(src)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        ans_src = brute_clique(src)
        ans_tgt = brute_independent_set(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("FAIL at", i, src, tgt, ans_src, ans_tgt)
            break
    return num, passed

if __name__ == "__main__":
    total, passed = run_tests()
    verified = total == passed
    verdict = {"verified": verified, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
