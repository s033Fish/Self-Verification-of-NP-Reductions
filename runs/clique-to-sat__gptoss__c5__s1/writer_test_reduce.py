import random
import itertools
import json
from problems import Clique, Sat
from reduce import reduce

def solve_clique(instance):
    n = instance['n']
    edges = set()
    for u, v in instance['edges']:
        edges.add(frozenset((u, v)))
    k = instance['k']
    # edge cases
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    # check all subsets of size >= k
    vertices = list(range(n))
    for size in range(k, n+1):
        for subset in itertools.combinations(vertices, size):
            ok = True
            for u, v in itertools.combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    ok = False
                    break
            if ok:
                return True
    return False

def solve_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # edge case: any empty clause => unsat
    for cl in clauses:
        if len(cl) == 0:
            return False
    # if no clauses, sat
    if not clauses:
        return True
    # brute force assignments
    for bits in range(1 << m):
        assign = [(bits >> i) & 1 == 1 for i in range(m)]
        good = True
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
                good = False
                break
        if good:
            return True
    return False

def random_instance(max_n=5, max_k=3):
    """Generate a small random Clique instance.
    The brute‑force SAT solver used in the tests enumerates all assignments,
    so we keep the number of variables (n * k) modest by limiting ``k``.
    """
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    edges: list[list[int]] = []
    for u, v in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    # k may be outside the valid range to test edge cases.
    k = random.randint(-1, max(max_n, max_k) + 2)
    # Clamp k to a small value for tractable SAT enumeration.
    if k > max_k:
        k = max_k
    return {"n": n, "edges": edges, "k": k}

def run_tests(num=200):
    passed = 0
    for _ in range(num):
        inst = random_instance()
        # validate
        Clique.validate(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        ans_clique = solve_clique(inst)
        ans_sat = solve_sat(sat_inst)
        if ans_clique == ans_sat:
            passed += 1
        else:
            print('Mismatch!')
            print('Clique instance:', json.dumps(inst))
            print('SAT instance:', json.dumps(sat_inst))
            print('Clique answer', ans_clique, 'SAT answer', ans_sat)
            break
    return passed, num

if __name__ == '__main__':
    passed, total = run_tests(300)
    print(f"Passed {passed}/{total} tests")
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
