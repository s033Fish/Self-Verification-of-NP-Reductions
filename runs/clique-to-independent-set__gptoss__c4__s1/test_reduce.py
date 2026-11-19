import itertools
import random
import json
from problems import Clique, IndependentSet
from reduce import reduce

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
    # check all subsets of size >= k
    for size in range(k, n+1):
        for subset in itertools.combinations(range(n), size):
            # check if every pair is an edge
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False

def solve_independent_set(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # any size >= k
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

def random_instance(max_n=6):
    n = random.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for u, v in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+2)  # include out of range values
    return {'n': n, 'edges': edges, 'k': k}

def main():
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_instance()
        # validate source
        Clique.validate(inst)
        # compute answers
        ans_clique = solve_clique(inst)
        red = reduce(inst)
        # validate target
        IndependentSet.validate(red)
        ans_ind = solve_independent_set(red)
        if ans_clique == ans_ind:
            passed += 1
        else:
            print('FAIL')
            print('orig', inst)
            print('reduced', red)
            print('clique', ans_clique, 'ind', ans_ind)
            break
    result = {
        "verified": passed == tests,
        "tests_run": tests,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
