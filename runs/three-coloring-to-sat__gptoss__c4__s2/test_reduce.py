import itertools
import random
import sys
from problems import ThreeColoring, Sat
from reduce import reduce

def three_coloring_bruteforce(instance):
    n = instance["n"]
    edges = instance["edges"]
    # assign colors 0,1,2
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
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assignment in itertools.product([False, True], repeat=m):
        # assignment is tuple indexed 0..m-1
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
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

def generate_random_graph(max_n=5, edge_prob=0.4):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}

def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        g = generate_random_graph()
        # Validate source
        ThreeColoring.validate(g)
        expected = three_coloring_bruteforce(g)
        sat_inst = reduce(g)
        Sat.validate(sat_inst)
        got = sat_bruteforce(sat_inst)
        if expected != got:
            print("Mismatch!", g, expected, got)
            sys.exit(1)
        passed += 1
    print(f"All {passed} tests passed.")
    return passed

if __name__ == "__main__":
    total = run_tests()
    # write verdict
    with open('verdict.json', 'w') as f:
        f.write('{"verified": true, "tests_run": %d, "tests_passed": %d}' % (total, total))
