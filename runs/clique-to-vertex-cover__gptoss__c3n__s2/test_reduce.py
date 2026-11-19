import itertools
import random
import json
import sys
from problems import Clique, VertexCover
from reduce import reduce

def solve_clique(inst):
    n = inst['n']
    edges = set(frozenset(e) for e in inst['edges'])
    k = inst['k']
    # Edge cases per definition
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # brute force
    for combo in itertools.combinations(range(n), k):
        ok = True
        for u, v in itertools.combinations(combo, 2):
            if frozenset((u, v)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def solve_vertex_cover(inst):
    n = inst['n']
    edges = [tuple(e) for e in inst['edges']]
    k = inst['k']
    # Edge cases
    if k < 0:
        return False
    if not edges:
        return k >= 0
    if k >= n:
        return True
    # brute force subsets up to size k
    for size in range(k+1):
        for subset in itertools.combinations(range(n), size):
            covered = True
            s = set(subset)
            for u, v in edges:
                if u not in s and v not in s:
                    covered = False
                    break
            if covered:
                return True
    return False

def random_instance(max_n=5):
    n = random.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for u, v in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+2)  # include out of range
    return {'n': n, 'edges': edges, 'k': k}

def main():
    random.seed(0)
    tests = 200
    passed = 0
    for i in range(tests):
        inst = random_instance()
        # validate input
        Clique.validate(inst)
        # solve source
        src_ans = solve_clique(inst)
        # reduce
        red = reduce(inst)
        # solve target
        tgt_ans = solve_vertex_cover(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch on instance', inst)
            print('Reduced to', red)
            print('src', src_ans, 'tgt', tgt_ans)
            sys.exit(1)
    verdict = {
        "verified": passed == tests,
        "tests_run": tests,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f, indent=2)
    print('All tests passed')

if __name__ == '__main__':
    main()
