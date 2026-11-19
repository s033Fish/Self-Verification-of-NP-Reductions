import random
import itertools
import json
from problems import Clique, Sat, InvalidInstance
from reduce import reduce

def solve_clique(instance):
    n = instance['n']
    edges = set()
    for u, v in instance['edges']:
        if u > v:
            u, v = v, u
        edges.add((u, v))
    k = instance['k']
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = range(n)
    for subset in itertools.combinations(vertices, k):
        ok = True
        for i in range(k):
            for j in range(i + 1, k):
                u, v = subset[i], subset[j]
                if u > v:
                    u, v = v, u
                if (u, v) not in edges:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            return True
    return False

def solve_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for clause in clauses:
        if len(clause) == 0:
            return False
    # enumerate assignments
    for bits in itertools.product([False, True], repeat=m):
        assign = {i + 1: bits[i] for i in range(m)}
        ok = True
        for clause in clauses:
            sat_clause = False
            for lit in clause:
                var = abs(lit)
                val = assign.get(var, False)
                if (lit > 0 and val) or (lit < 0 and not val):
                    sat_clause = True
                    break
            if not sat_clause:
                ok = False
                break
        if ok:
            return True
    return False

def random_instance(max_n=4):
    """Generate a small random Clique instance.

    The brute‑force SAT solver enumerates all assignments, so we keep the number of
    variables low by limiting n and ensuring k does not exceed n when n>0.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = []
    for (u, v) in possible_edges:
        if random.choice([True, False]):
            edges.append([u, v])
    if n == 0:
        k = random.randint(-2, 2)
    else:
        k = random.randint(-2, n)
    return {"n": n, "edges": edges, "k": k}

def main():
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_instance()
        try:
            Clique.validate(inst)
        except InvalidInstance:
            continue
        clique_ans = solve_clique(inst)
        sat_inst = reduce(inst)
        Sat.validate(sat_inst)
        sat_ans = solve_sat(sat_inst)
        if clique_ans != sat_ans:
            print('Mismatch!')
            print('Clique instance', inst)
            print('Clique ans', clique_ans)
            print('SAT instance', sat_inst)
            print('SAT ans', sat_ans)
            break
        passed += 1
    result = {"verified": passed == tests, "tests_run": tests, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(result, f)
    print('Done', result)

if __name__ == '__main__':
    main()
