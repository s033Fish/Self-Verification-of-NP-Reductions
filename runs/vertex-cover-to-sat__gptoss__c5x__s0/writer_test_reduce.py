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
    if not edges:
        return True  # empty graph always yes
    if k >= n:
        return True
    vertices = list(range(n))
    for r in range(k + 1):
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


def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause makes unsat
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


def random_instance(max_n=5, max_edges=7, max_k=5):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    random.shuffle(possible_edges)
    m = random.randint(0, min(len(possible_edges), max_edges))
    edges = [list(e) for e in possible_edges[:m]]
    k = random.randint(-1, max_k)
    return {"n": n, "edges": edges, "k": k}


def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_instance()
        # validate source
        VertexCover.validate(inst)
        vc_ans = vertex_cover_bruteforce(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        sat_ans = sat_bruteforce(sat_inst)
        if vc_ans == sat_ans:
            passed += 1
        else:
            print('FAIL')
            print('Instance:', json.dumps(inst))
            print('VC:', vc_ans, 'SAT:', sat_ans)
            print('Reduced SAT:', json.dumps(sat_inst))
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(500)
    print(f"Tests passed: {passed}/{total}")
    # write verdict
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
