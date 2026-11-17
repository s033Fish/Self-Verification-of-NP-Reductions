import itertools
import json
from problems import ThreeColoring, OneInThreeSat
from reduce import reduce

def three_coloring_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False

def one_in_three_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            true_cnt = sum(assign[abs(lit)-1] for lit in clause)
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False

def all_graphs(n):
    vertices = list(range(n))
    possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
    for mask in range(1 << len(possible_edges)):
        edges = []
        for idx, (i, j) in enumerate(possible_edges):
            if mask & (1 << idx):
                edges.append([i, j])
        yield {'n': n, 'edges': edges}

def run_tests():
    total = 0
    passed = 0
    # limit n to 3 for feasible brute force
    for n in range(0, 4):
        for G in all_graphs(n):
            total += 1
            ThreeColoring.validate(G)
            src_ans = three_coloring_bruteforce(G)
            red = reduce(G)
            OneInThreeSat.validate(red)
            tgt_ans = one_in_three_bruteforce(red)
            if src_ans == tgt_ans:
                passed += 1
            else:
                print('FAIL', G, src_ans, tgt_ans)
                return False, total, passed
    return True, total, passed

if __name__ == '__main__':
    ok, total, passed = run_tests()
    print('All tests passed?', ok, 'total', total, 'passed', passed)
    verdict = {'verified': ok, 'tests_run': total, 'tests_passed': passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
