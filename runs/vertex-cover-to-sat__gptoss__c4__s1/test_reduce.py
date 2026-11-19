import random
import itertools
import json
import sys
from problems import VertexCover, Sat
from reduce import reduce


def solve_vertex_cover(inst):
    n = inst['n']
    edges = inst['edges']
    k = inst['k']
    if k < 0:
        return False
    # trivial yes cases handled by brute force anyway
    vertices = list(range(n))
    for r in range(0, min(k, n) + 1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            s = set(subset)
            for u, v in edges:
                if u not in s and v not in s:
                    covered = False
                    break
            if covered:
                return True
    return False


def solve_sat(inst):
    m = inst['num_vars']
    clauses = inst['clauses']
    # empty clause -> unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
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


def random_instance(max_n=5, max_edges=10, max_k=5):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    m = random.randint(0, min(len(possible_edges), max_edges))
    edges = random.sample(possible_edges, m)
    k = random.randint(-1, max_k)
    return {"n": n, "edges": [list(e) for e in edges], "k": k}


def main():
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_instance()
        # validate
        VertexCover.validate(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        vc_ans = solve_vertex_cover(inst)
        sat_ans = solve_sat(sat_inst)
        if vc_ans == sat_ans:
            passed += 1
        else:
            print('FAIL')
            print('VertexCover instance:', json.dumps(inst))
            print('Reduced SAT instance:', json.dumps(sat_inst))
            print('VC answer', vc_ans, 'SAT answer', sat_ans)
            sys.exit(1)
    print('All tests passed', passed, '/', tests)
    # write verdict
    with open('verdict.json', 'w') as f:
        json.dump({"verified": True, "tests_run": tests, "tests_passed": passed}, f)

if __name__ == '__main__':
    main()
