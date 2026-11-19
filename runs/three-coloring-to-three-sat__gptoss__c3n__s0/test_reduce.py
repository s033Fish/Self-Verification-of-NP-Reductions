import itertools
import random
import json
from problems import ThreeColoring, ThreeSat
from reduce import reduce


def solve_three_coloring(instance):
    n = instance["n"]
    edges = instance["edges"]
    for colors in itertools.product(range(3), repeat=n):
        if all(colors[u] != colors[v] for u, v in edges):
            return True
    return False


def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for vals in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            sat = False
            for lit in clause:
                var = abs(lit) - 1
                sign = lit > 0
                if vals[var] == sign:
                    sat = True
                    break
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False


def random_graph(max_n=3, edge_prob=0.4):
    n = random.randint(0, max_n)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < edge_prob:
                edges.append([i, j])
    return {"n": n, "edges": edges}


def run_tests(num=30):
    passed = 0
    for _ in range(num):
        inst = random_graph()
        ThreeColoring.validate(inst)
        red = reduce(inst)
        ThreeSat.validate(red)
        ans_src = solve_three_coloring(inst)
        ans_tgt = solve_three_sat(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", json.dumps(inst), json.dumps(red))
            break
    return passed, num

if __name__ == "__main__":
    passed, total = run_tests(30)
    print(f"Passed {passed}/{total} tests")
