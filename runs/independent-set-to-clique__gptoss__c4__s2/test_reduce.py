import random
import itertools
import json
from problems import IndependentSet, Clique
from reduce import reduce


def independent_set_bruteforce(inst):
    n = inst['n']
    edges = set(frozenset((u, v)) for u, v in inst['edges'])
    k = inst['k']
    if k <= 0:
        return True
    if k > n:
        return False
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


def clique_bruteforce(inst):
    n = inst['n']
    edges = set(frozenset((u, v)) for u, v in inst['edges'])
    k = inst['k']
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
    possible = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for (i, j) in possible:
        if random.choice([True, False]):
            edges.append([i, j])
    k = random.randint(-1, n+2)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_instance()
        # validate source
        IndependentSet.validate(src)
        src_ans = independent_set_bruteforce(src)
        tgt = reduce(src)
        Clique.validate(tgt)
        tgt_ans = clique_bruteforce(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('FAIL')
            print('src', src)
            print('src_ans', src_ans)
            print('tgt', tgt)
            print('tgt_ans', tgt_ans)
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
