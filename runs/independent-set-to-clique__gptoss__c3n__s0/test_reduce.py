import random
import itertools
import json
import sys
from problems import IndependentSet, Clique
from reduce import reduce

def independent_set_bruteforce(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # enumerate subsets
    for r in range(k, n+1):
        for subset in itertools.combinations(range(n), r):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False

def clique_bruteforce(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    for r in range(k, n+1):
        for subset in itertools.combinations(range(n), r):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for (u, v) in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+2)  # allow out of range values
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_instance()
        # validate source
        try:
            IndependentSet.validate(src)
        except Exception as e:
            # skip invalid generated instances (should not happen)
            continue
        src_ans = independent_set_bruteforce(src)
        tgt = reduce(src)
        # validate target
        try:
            Clique.validate(tgt)
        except Exception as e:
            print("Target validation failed", e, file=sys.stderr)
            return False, passed
        tgt_ans = clique_bruteforce(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", src, src_ans, tgt, tgt_ans)
            return False, passed
    return True, passed

if __name__ == "__main__":
    ok, passed = run_tests(500)
    result = {
        "verified": ok,
        "tests_run": 500,
        "tests_passed": passed
    }
    print(json.dumps(result))
    sys.exit(0 if ok else 1)
