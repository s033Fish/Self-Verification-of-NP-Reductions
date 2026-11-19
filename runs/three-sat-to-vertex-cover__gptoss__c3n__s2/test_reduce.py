import itertools
import random
import json
from problems import ThreeSat, VertexCover
from reduce import reduce

def solve_three_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # variable i+1
        ok = True
        for clause in clauses:
            sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    sat = True
                if lit < 0 and not val:
                    sat = True
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
    # if k < 0: return False
    if k < 0:
        return False
    # brute force all subsets up to k
    for r in range(k + 1):
        for subset in itertools.combinations(range(n), r):
            covered = True
            s = set(subset)
            for u, v in edges:
                if u not in s and v not in s:
                    covered = False
                    break
            if covered:
                return True
    return False

def random_three_sat(max_vars=4, max_clauses=4):
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses according to edge case, but not required for brute test
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        # pick 3 distinct vars from 1..max(m,3) ensuring m>=3 if clauses>0
        if m < 3:
            # need at least 3 vars for a clause, set m=3
            m = 3
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}

def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        inst = random_three_sat()
        # validate source
        ThreeSat.validate(inst)
        reduced = reduce(inst)
        VertexCover.validate(reduced)
        ans_src = solve_three_sat(inst)
        ans_tgt = solve_vertex_cover(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch!')
            print('Source:', inst)
            print('Reduced:', reduced)
            print('Source answer', ans_src, 'Target answer', ans_tgt)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests()
    result = {
        'verified': passed == total,
        'tests_run': total,
        'tests_passed': passed,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
