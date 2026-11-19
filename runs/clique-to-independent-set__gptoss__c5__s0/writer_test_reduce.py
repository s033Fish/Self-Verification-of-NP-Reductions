import random
import itertools
import json
from problems import Clique, IndependentSet
from reduce import reduce


def solve_clique(inst):
    n = inst["n"]
    edges = set(frozenset(e) for e in inst["edges"])
    k = inst["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # brute force all subsets of size >= k
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def solve_independent_set(inst):
    n = inst["n"]
    edges = set(frozenset(e) for e in inst["edges"])
    k = inst["k"]
    if k <= 0:
        return True
    if k > n:
        return False
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


def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for u, v in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+2)  # allow out of range values
    return {"n": n, "edges": edges, "k": k}


def main():
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_instance()
        # validate instance (may raise)
        try:
            Clique.validate(inst)
        except Exception as e:
            # skip malformed instances (should not happen)
            continue
        reduced = reduce(inst)
        # Both should be valid
        IndependentSet.validate(reduced)
        ans_src = solve_clique(inst)
        ans_tgt = solve_independent_set(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch on instance", inst)
            print("Reduced", reduced)
            print(ans_src, ans_tgt)
            break
    verdict = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
