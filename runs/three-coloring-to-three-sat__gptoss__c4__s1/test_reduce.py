import random
import sys
from itertools import product
from problems import ThreeColoring, ThreeSat, InvalidInstance
from reduce import reduce

def solve_three_coloring(instance):
    ThreeColoring.validate(instance)
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    for coloring in product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False

def solve_three_sat(instance):
    """Backtracking SAT solver for 3‑SAT instances.

    Uses simple DFS with early clause pruning; sufficient for the small
    instances generated in the tests.
    """
    ThreeSat.validate(instance)
    m = instance['num_vars']
    clauses = instance['clauses']
    proc_clauses = []
    for cl in clauses:
        proc_clauses.append([(abs(lit) - 1, lit > 0) for lit in cl])
    assignment = [None] * m
    def backtrack(idx: int) -> bool:
        if idx == m:
            for cl in proc_clauses:
                if not any((assignment[v] if pos else not assignment[v]) for v, pos in cl):
                    return False
            return True
        for val in (False, True):
            assignment[idx] = val
            early_fail = False
            for cl in proc_clauses:
                clause_sat = False
                for v, pos in cl:
                    a = assignment[v]
                    if a is None:
                        clause_sat = True
                        break
                    if a if pos else not a:
                        clause_sat = True
                        break
                if not clause_sat:
                    early_fail = True
                    break
            if not early_fail and backtrack(idx + 1):
                return True
        assignment[idx] = None
        return False
    return backtrack(0)

def random_graph(max_n=2, edge_prob=0.4):
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}

def run_tests(num=200):
    for i in range(num):
        inst = random_graph()
        ThreeColoring.validate(inst)
        sat_inst = reduce(inst)
        ThreeSat.validate(sat_inst)
        res1 = solve_three_coloring(inst)
        res2 = solve_three_sat(sat_inst)
        if res1 != res2:
            print('Mismatch on instance', inst)
            print('SAT instance', sat_inst)
            print('3-color result', res1, 'SAT result', res2)
            sys.exit(1)
    print('All', num, 'random tests passed')

if __name__ == '__main__':
    run_tests()
