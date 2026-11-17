import itertools
import random
import json
from problems import ThreeColoring, Sat
from reduce import reduce

def solve_three_coloring(instance):
    n = instance['n']
    edges = instance['edges']
    # iterate over all assignments of colors 0,1,2 to each vertex
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False

def solve_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for vals in itertools.product([False, True], repeat=m):
        assignment = {i+1: vals[i] for i in range(m)}
        satisfied = True
        for clause in clauses:
            # empty clause is unsatisfiable
            if len(clause) == 0:
                satisfied = False
                break
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
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
    for _ in range(num_trials):
        inst = random_graph()
        # validate source
        ThreeColoring.validate(inst)
        red = reduce(inst)
        Sat.validate(red)
        ans_src = solve_three_coloring(inst)
        ans_red = solve_sat(red)
        if ans_src == ans_red:
            passed += 1
        else:
            print('Mismatch!')
            print('source', inst)
            print('reduced', red)
            print('src ans', ans_src, 'red ans', ans_red)
            break
    return passed, num_trials

if __name__ == '__main__':
    passed, total = run_tests(200)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
