import itertools
import random
import json
import sys
from pathlib import Path

# Import the reduction and problem definitions
from reduce import reduce
import problems

def vertex_cover_bruteforce(instance):
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    # any subset of vertices size <= k
    for size in range(k+1):
        for subset in itertools.combinations(range(n), size):
            covered = True
            for u,v in edges:
                if u not in subset and v not in subset:
                    covered = False
                    break
            if covered:
                return True
    return False

def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # empty clause -> unsat immediately
    for cl in clauses:
        if len(cl) == 0:
            return False
    for assignment in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
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

def random_vertex_cover_instance(max_n=5, max_edges=7, max_k=5):
    n = random.randint(0, max_n)
    possible_edges = [(i,j) for i in range(n) for j in range(i+1, n)]
    random.shuffle(possible_edges)
    ecount = random.randint(0, min(len(possible_edges), max_edges))
    edges = [list(possible_edges[i]) for i in range(ecount)]
    k = random.randint(-1, max_k)
    return {"n": n, "edges": edges, "k": k}

def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        src = random_vertex_cover_instance()
        # validate source
        problems.VertexCover.validate(src)
        # reduce
        tgt = reduce(src)
        problems.Sat.validate(tgt)
        src_ans = vertex_cover_bruteforce(src)
        tgt_ans = sat_bruteforce(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", src, src_ans, tgt, tgt_ans)
            return False, passed
    return True, passed

if __name__ == "__main__":
    ok, passed = run_tests()
    result = {"verified": ok, "tests_run": 200, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print(json.dumps(result))
    sys.exit(0 if ok else 1)
