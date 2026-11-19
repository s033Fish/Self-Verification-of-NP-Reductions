import itertools
import json
import random
import sys
from pathlib import Path

# Import the problems and reduction
import problems
from reduce import reduce

def three_coloring_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    # iterate over assignments of 0,1,2 for each vertex
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for assign in itertools.product([False, True], repeat=m):
        # assign is tuple indexed 0..m-1 corresponding to var 1..m
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def generate_all_graphs(max_n):
    # generate all simple undirected graphs without self loops, up to max_n vertices
    for n in range(max_n+1):
        vertices = list(range(n))
        possible_edges = [(i,j) for i in range(n) for j in range(i+1,n)]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for idx, (u,v) in enumerate(possible_edges):
                if mask & (1<<idx):
                    edges.append([u,v])
            yield {'n': n, 'edges': edges}

def test_random_graphs(num_tests=200, max_n=5):
    for _ in range(num_tests):
        n = random.randint(0, max_n)
        # generate random edge set
        edges = []
        for i in range(n):
            for j in range(i+1, n):
                if random.choice([True, False]):
                    edges.append([i,j])
        instance = {'n': n, 'edges': edges}
        # validate
        problems.ThreeColoring.validate(instance)
        red = reduce(instance)
        problems.Sat.validate(red)
        src = three_coloring_bruteforce(instance)
        tgt = sat_bruteforce(red)
        if src != tgt:
            print('Mismatch on instance', instance)
            print('Reduced to', red)
            print('src', src, 'tgt', tgt)
            return False
    return True

def main():
    # exhaustive test for n up to 4 (since 3^4=81, manageable)
    for inst in generate_all_graphs(4):
        problems.ThreeColoring.validate(inst)
        red = reduce(inst)
        problems.Sat.validate(red)
        src = three_coloring_bruteforce(inst)
        tgt = sat_bruteforce(red)
        if src != tgt:
            print('FAIL on', inst)
            sys.exit(1)
    # random tests up to n=6
    if not test_random_graphs(200, 6):
        sys.exit(1)
    print('All tests passed')
    # write verdict
    verdict = {"verified": True, "tests_run": 1, "tests_passed": 1}
    Path('verdict.json').write_text(json.dumps(verdict))

if __name__ == '__main__':
    main()
