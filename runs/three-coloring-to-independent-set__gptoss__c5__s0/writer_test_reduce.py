import itertools
import random
import json
from problems import ThreeColoring, IndependentSet
from reduce import reduce

def solve_three_coloring(inst):
    n = inst['n']
    edges = [(u, v) for u, v in inst['edges']]
    # iterate over assignments of 0,1,2 colors
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False

def solve_independent_set(inst):
    n = inst['n']
    k = inst['k']
    edges = set(frozenset((u, v)) for u, v in inst['edges'])
    # check subsets of size >= k
    for r in range(k, n+1):
        for subset in itertools.combinations(range(n), r):
            good = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    good = False
                    break
            if good:
                return True
    return False

def random_graph(max_n=5, edge_prob=0.3):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {'n': n, 'edges': edges}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        src = random_graph()
        # validate source
        ThreeColoring.validate(src)
        src_ans = solve_three_coloring(src)
        tgt = reduce(src)
        IndependentSet.validate(tgt)
        tgt_ans = solve_independent_set(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('src', src)
            print('src_ans', src_ans)
            print('tgt', tgt)
            print('tgt_ans', tgt_ans)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    result = {
        'verified': passed == total,
        'tests_run': total,
        'tests_passed': passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
