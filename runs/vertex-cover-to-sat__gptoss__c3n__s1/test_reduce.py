import itertools
import random
import json
import sys
from problems import VertexCover, Sat
from reduce import reduce

# Brute-force solver for Vertex Cover
def solve_vertex_cover(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    # any subset of vertices of size <= k
    for r in range(k+1):
        for subset in itertools.combinations(range(n), r):
            covered = True
            for u,v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False

# Brute-force SAT solver
def solve_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause -> unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
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
    return True if not clauses else False


def random_instance(max_n=5):
    n = random.randint(0, max_n)
    # generate random edges without duplicates
    possible = [(i,j) for i in range(n) for j in range(i+1,n)]
    edges = []
    for (i,j) in possible:
        if random.random() < 0.3:
            edges.append([i,j])
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}


def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_instance()
        # Validate source
        try:
            VertexCover.validate(inst)
        except Exception as e:
            print('Invalid source instance', inst, e)
            continue
        src_ans = solve_vertex_cover(inst)
        red = reduce(inst)
        # Validate target
        try:
            Sat.validate(red)
        except Exception as e:
            print('Invalid reduced instance', red, e)
            continue
        tgt_ans = solve_sat(red)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('src', inst, src_ans)
            print('red', red, tgt_ans)
            break
    print('Tests run', total, 'passed', passed)
    # write verdict
    verdict = {
        "verified": total==passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json','w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
