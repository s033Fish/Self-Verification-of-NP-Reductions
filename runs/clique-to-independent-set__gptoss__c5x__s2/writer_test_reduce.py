import random
import itertools
import json
from problems import Clique, IndependentSet
from reduce import reduce

def brute_clique(instance):
    n = instance['n']
    edges = set(tuple(sorted(e)) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check all subsets of size >= k
    for size in range(k, n+1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if (u, v) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False

def brute_independent(instance):
    n = instance['n']
    edges = set(tuple(sorted(e)) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    for size in range(k, n+1):
        for subset in itertools.combinations(range(n), size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if (u, v) in edges:
                    ok = False
                    break
            if ok:
                return True
    return False


def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for u, v in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+2)  # include edge cases
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_instance()
        # validate source
        Clique.validate(src)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        ans_src = brute_clique(src)
        ans_tgt = brute_independent(tgt)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('FAIL')
            print('src', src)
            print('tgt', tgt)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            break
    return passed

if __name__ == '__main__':
    passed = run_tests(500)
    result = {
        "verified": passed == 500,
        "tests_run": 500,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
