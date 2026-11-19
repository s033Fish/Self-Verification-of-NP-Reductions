import random
import itertools
import json
from problems import VertexCover, Sat, InvalidInstance
from reduce import reduce


def vertex_cover_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    # any subset up to k
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause -> unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # index 0 -> var1
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


def generate_random_instance(max_n=5):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    edges = []
    for (u, v) in possible_edges:
        if random.random() < 0.3:
            edges.append([u, v])
    k = random.randint(-1, n + 1)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num_trials=200):
    passed = 0
    for _ in range(num_trials):
        inst = generate_random_instance()
        # validate source
        try:
            VertexCover.validate(inst)
        except InvalidInstance:
            continue  # shouldn't happen
        reduced = reduce(inst)
        # validate target
        Sat.validate(reduced)
        ans_src = vertex_cover_bruteforce(inst)
        ans_tgt = sat_bruteforce(reduced)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch')
            print('src', inst, ans_src)
            print('tgt', reduced, ans_tgt)
            return False, passed
    return True, passed

if __name__ == '__main__':
    ok, count = run_tests(500)
    result = {
        "verified": ok,
        "tests_run": 500,
        "tests_passed": count if ok else count,
    }
    print(json.dumps(result))
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
