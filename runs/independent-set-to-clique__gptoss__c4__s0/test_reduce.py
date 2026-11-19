import itertools
import random
import json
from problems import IndependentSet, Clique
from reduce import reduce

def solve_independent_set(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # brute force all subsets of size >= k
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

def solve_clique(instance):
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

def random_instance(max_n=6):
    n = random.randint(0, max_n)
    # generate all possible edges
    possible = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for u, v in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+2)  # allow out of range
    return {"n": n, "edges": edges, "k": k}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_instance()
        # Validate source and target formats
        IndependentSet.validate(inst)
        reduced = reduce(inst)
        Clique.validate(reduced)
        ans_src = solve_independent_set(inst)
        ans_tgt = solve_clique(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('FAIL')
            print('src', inst)
            print('reduced', reduced)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
