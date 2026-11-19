import itertools
import random
import json
from problems import ThreeColoring, Sat
from reduce import reduce

def three_coloring_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return n == 0  # empty graph is yes (handled by loop)

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for assignment in itertools.product([False, True], repeat=m):
        sat = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                sat = False
                break
        if sat:
            return True
    # No assignment works; also handle case of zero clauses which is trivially true
    return len(clauses) == 0


def generate_random_graph(max_n=5, edge_prob=0.4):
    n = random.randint(0, max_n)
    edges = []
    seen = set()
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
                seen.add(frozenset((u, v)))
    return {'n': n, 'edges': edges}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        src = generate_random_graph()
        # Validate source
        ThreeColoring.validate(src)
        src_ans = three_coloring_bruteforce(src)
        sat_inst = reduce(src)
        Sat.validate(sat_inst)
        tgt_ans = sat_bruteforce(sat_inst)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('src', src)
            print('src_ans', src_ans)
            print('sat_inst', sat_inst)
            print('tgt_ans', tgt_ans)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests()
    result = {
        'verified': passed == total,
        'tests_run': total,
        'tests_passed': passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
