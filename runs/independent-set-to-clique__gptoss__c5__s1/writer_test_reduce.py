import itertools
import random
import json
from problems import IndependentSet, Clique
from reduce import reduce


def independent_set_bruteforce(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # iterate subsets of vertices
    for size in range(k, n+1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def clique_bruteforce(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    for size in range(k, n+1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def random_instance(max_n=5):
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for u, v in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+2)  # allow out-of-range values
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_instance()
        # Validate source
        try:
            IndependentSet.validate(src)
        except Exception:
            # Invalid instances are not required to be handled; skip
            continue
        tgt = reduce(src)
        # Validate target
        Clique.validate(tgt)
        src_ans = independent_set_bruteforce(src)
        tgt_ans = clique_bruteforce(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('src', src)
            print('tgt', tgt)
            print('src_ans', src_ans, 'tgt_ans', tgt_ans)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
