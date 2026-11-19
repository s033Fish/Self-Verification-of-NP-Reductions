import itertools
import random
import json
from problems import ThreeColoring, ThreeSat
from reduce import reduce


def solve_three_coloring(instance):
    n = instance["n"]
    edges = instance["edges"]
    # iterate over all assignments of colors 0,1,2
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
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i+1: bits[i] for i in range(m)}
        sat = True
        for clause in clauses:
            # clause is list of three literals
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
                sat = False
                break
        if sat:
            return True
    return False


def generate_all_graphs(max_n=4):
    # generate all graphs up to max_n vertices
    for n in range(max_n+1):
        vertices = list(range(n))
        possible_edges = [(i,j) for i in vertices for j in vertices if i<j]
        for mask in range(1<<len(possible_edges)):
            edges = []
            for idx, (u,v) in enumerate(possible_edges):
                if mask & (1<<idx):
                    edges.append([u,v])
            yield {"n": n, "edges": edges}


def run_tests():
    total = 0
    passed = 0
    for instance in generate_all_graphs(4):
        # validate source
        ThreeColoring.validate(instance)
        src_ans = solve_three_coloring(instance)
        red = reduce(instance)
        ThreeSat.validate(red)
        tgt_ans = solve_three_sat(red)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", instance, src_ans, tgt_ans)
            break
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
