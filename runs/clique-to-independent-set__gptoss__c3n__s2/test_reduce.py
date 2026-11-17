import random
import itertools
import json
import sys
import problems
from reduce import reduce

def brute_clique(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
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
            # check all pairs have edge
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False

def brute_independent(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
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

def random_instance(n, edge_prob=0.5, k_range=(-1, None)):
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    if k_range[1] is None:
        k_max = n+1
    else:
        k_max = k_range[1]
    k = random.randint(k_range[0], k_max)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num_tests=200):
    passed = 0
    total = 0
    for _ in range(num_tests):
        n = random.randint(0, 5)
        inst = random_instance(n, edge_prob=0.5, k_range=(-2, n+2))
        # validate source
        try:
            problems.Clique.validate(inst)
        except Exception as e:
            # skip malformed (shouldn't happen)
            continue
        reduced = reduce(inst)
        # validate target
        problems.IndependentSet.validate(reduced)
        ans_src = brute_clique(inst)
        ans_tgt = brute_independent(reduced)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch!')
            print('src', inst, ans_src)
            print('tgt', reduced, ans_tgt)
            break
    return total, passed

if __name__ == '__main__':
    total, passed = run_tests(500)
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
