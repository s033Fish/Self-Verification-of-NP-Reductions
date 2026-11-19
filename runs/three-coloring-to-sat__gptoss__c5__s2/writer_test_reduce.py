import itertools
import json
import sys
from typing import List, Dict

from problems import ThreeColoring, Sat
from reduce import reduce


def three_coloring_bruteforce(instance: Dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    # iterate over assignments of 0,1,2 to n vertices
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # assignments as booleans for variables 1..m
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # empty clause is unsatisfiable
            if len(clause) == 0:
                ok = False
                break
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


def generate_graphs(max_n: int) -> List[Dict]:
    graphs = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for r in range(len(possible_edges) + 1):
            for edges in itertools.combinations(possible_edges, r):
                # format edges as lists
                instance = {"n": n, "edges": [list(e) for e in edges]}
                # validate
                ThreeColoring.validate(instance)
                graphs.append(instance)
    return graphs


def main():
    max_n = 4  # small enough for brute force
    graphs = generate_graphs(max_n)
    total = len(graphs)
    passed = 0
    for g in graphs:
        src_ans = three_coloring_bruteforce(g)
        sat_instance = reduce(g)
        tgt_ans = sat_bruteforce(sat_instance)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", g, src_ans, tgt_ans, file=sys.stderr)
            break
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
