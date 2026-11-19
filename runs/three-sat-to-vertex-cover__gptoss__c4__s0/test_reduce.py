import itertools
import random
import json
from problems import ThreeSat, VertexCover
from reduce import reduce

def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i+1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            # clause satisfied if any literal true
            sat = False
            for lit in clause:
                var = abs(lit)
                val = assignment[var]
                if lit > 0 and val:
                    sat = True
                if lit < 0 and not val:
                    sat = True
                if sat:
                    break
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False

def solve_vertex_cover(instance):
    n = instance['n']
    edges = [tuple(e) for e in instance['edges']]
    k = instance['k']
    # if k < 0 immediate false
    if k < 0:
        return False
    # brute force all subsets up to k
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            s = set(subset)
            for u,v in edges:
                if u not in s and v not in s:
                    covered = False
                    break
            if covered:
                return True
    return False

def random_three_sat(max_vars=4, max_clauses=4):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if clauses exist
    c = random.randint(0, max_clauses)
    clauses = []
    for _ in range(c):
        # pick 3 distinct variables from 1..max(m,3)
        if m < 3:
            # need at least 3 variables for a clause, so increase m
            m = 3
        vars_ = random.sample(range(1, m+1), 3)
        clause = []
        for v in vars_:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        inst = random_three_sat()
        # validate source
        ThreeSat.validate(inst)
        vc = reduce(inst)
        VertexCover.validate(vc)
        ans_src = solve_three_sat(inst)
        ans_tgt = solve_vertex_cover(vc)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch on test', i)
            print('3SAT:', inst)
            print('VC:', vc)
            print('src ans', ans_src, 'tgt ans', ans_tgt)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests()
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(result, indent=2))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
