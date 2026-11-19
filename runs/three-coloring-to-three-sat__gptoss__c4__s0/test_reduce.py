import itertools
import json
from reduce import reduce as reduce_instance
from problems import ThreeColoring, ThreeSat, InvalidInstance

def solve_three_coloring(instance):
    n = instance["n"]
    edges = instance["edges"]
    for colors in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if colors[u] == colors[v]:
                ok = False
                break
        if ok:
            return True
    return False

def solve_three_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assign in itertools.product([False, True], repeat=m):
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

def all_graphs(n):
    vertices = list(range(n))
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    for mask in range(1 << len(possible_edges)):
        edges = []
        for idx, (u, v) in enumerate(possible_edges):
            if mask & (1 << idx):
                edges.append([u, v])
        yield {"n": n, "edges": edges}


def run_tests():
    total = 0
    passed = 0
    for n in range(0, 5):  # up to 4 vertices
        for graph in all_graphs(n):
            total += 1
            try:
                ThreeColoring.validate(graph)
            except InvalidInstance as e:
                print("Invalid graph", graph, e)
                continue
            col_ans = solve_three_coloring(graph)
            red = reduce_instance(graph)
            ThreeSat.validate(red)
            sat_ans = solve_three_sat(red)
            if col_ans == sat_ans:
                passed += 1
            else:
                print("Mismatch!", graph, col_ans, sat_ans)
    # Edge case K4
    k4 = {"n": 4, "edges": [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]}
    total += 1
    col_ans = solve_three_coloring(k4)
    red = reduce_instance(k4)
    sat_ans = solve_three_sat(red)
    if col_ans == sat_ans:
        passed += 1
    else:
        print("Mismatch K4", col_ans, sat_ans)
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    print(f"Tests run: {total}, passed: {passed}")
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
