import itertools
import random
import json
from problems import VertexCover, Sat
from reduce import reduce

def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    # if no edges, always yes
    if not edges:
        return True
    # if k >= n, always yes
    if k >= n:
        return True
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            cover = set(subset)
            ok = True
            for u,v in edges:
                if u not in cover and v not in cover:
                    ok = False
                    break
            if ok:
                return True
    return False

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty formula is satisfiable
    if not clauses:
        return True
    # if any empty clause, unsat
    for cl in clauses:
        if len(cl) == 0:
            return False
    for assignment in itertools.product([False, True], repeat=m):
        # assignment is tuple indexed 0..m-1 for vars 1..m
        sat = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
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

def random_instance(max_n=5, max_edges=10):
    n = random.randint(0, max_n)
    possible = [(i,j) for i in range(n) for j in range(i+1,n)]
    edges = []
    random.shuffle(possible)
    for _ in range(random.randint(0, min(len(possible), max_edges))):
        edges.append(list(possible.pop()))
    k = random.randint(-1, max(n,2))
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_instance()
        # validate source
        try:
            VertexCover.validate(inst)
        except Exception as e:
            print('Invalid source instance', inst, e)
            continue
        src_ans = vertex_cover_bruteforce(inst)
        red = reduce(inst)
        # validate target
        try:
            Sat.validate(red)
        except Exception as e:
            print('Invalid reduced instance', red, e)
            continue
        tgt_ans = sat_bruteforce(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('src', inst, src_ans)
            print('red', red, tgt_ans)
            return passed, False
    return passed, True

if __name__ == '__main__':
    total = 200
    passed, ok = run_tests(total)
    verdict = {"verified": ok, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    with open('verdict.json','w') as f:
        json.dump(verdict, f)
