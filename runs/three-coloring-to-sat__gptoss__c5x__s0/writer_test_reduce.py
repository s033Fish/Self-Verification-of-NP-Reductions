import json
import random
import itertools
import os
from problems import ThreeColoring, Sat
from reduce import reduce

def three_coloring_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    # Edge cases covered by brute force anyway
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for assignment in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # empty clause is unsatisfied
            if not clause:
                ok = False
                break
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
                ok = False
                break
        if ok:
            return True
    return False

def random_graph(max_n=5):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = []
    for (u, v) in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    return {"n": n, "edges": edges}

def run_tests(num_trials=200):
    passed = 0
    total = 0
    for _ in range(num_trials):
        inst = random_graph()
        # ensure valid instance
        ThreeColoring.validate(inst)
        src_ans = three_coloring_bruteforce(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        tgt_ans = sat_bruteforce(sat_inst)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('Instance:', json.dumps(inst))
            print('Source answer', src_ans, 'Target answer', tgt_ans)
            break
        total += 1
    # Test edge cases explicitly
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 3, "edges": []},
        {"n": 4, "edges": [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]},  # K4
    ]
    for inst in edge_cases:
        ThreeColoring.validate(inst)
        src_ans = three_coloring_bruteforce(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        tgt_ans = sat_bruteforce(sat_inst)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch edge case', inst)
            print(src_ans, tgt_ans)
            break
        total += 1
    return passed, total

if __name__ == '__main__':
    passed, total = run_tests()
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print(json.dumps(result, indent=2))
