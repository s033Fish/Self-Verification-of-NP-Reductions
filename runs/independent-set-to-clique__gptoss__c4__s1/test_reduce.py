import random
import itertools
import json
from problems import IndependentSet, Clique, InvalidInstance
from reduce import reduce

def independent_set_bruteforce(instance):
    IndependentSet.validate(instance)
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    k = instance['k']
    if k <= 0:
        return True
    if k > n:
        return False
    # check all subsets of size >= k
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
    Clique.validate(instance)
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

def random_graph(n, edge_prob=0.5):
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return edges

def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        n = random.randint(0, 6)
        edges = random_graph(n, edge_prob=0.4)
        k = random.randint(-2, n+2)
        instance = {'n': n, 'edges': edges, 'k': k}
        try:
            ind_ans = independent_set_bruteforce(instance)
            red = reduce(instance)
            clique_ans = clique_bruteforce(red)
            if ind_ans != clique_ans:
                print('Mismatch!')
                print('Original:', json.dumps(instance))
                print('Reduced:', json.dumps(red))
                print('IndependentSet answer', ind_ans)
                print('Clique answer', clique_ans)
                return False, passed
        except InvalidInstance as e:
            print('Invalid instance generated?', e)
            return False, passed
        passed += 1
    return True, passed

if __name__ == '__main__':
    ok, count = run_tests(500)
    result = {
        'verified': ok,
        'tests_run': count,
        'tests_passed': count if ok else count-1,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
