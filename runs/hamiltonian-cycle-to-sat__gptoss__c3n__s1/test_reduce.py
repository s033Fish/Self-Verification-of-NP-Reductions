import itertools
import random
import json
from problems import HamiltonianCycle, Sat
from reduce import reduce


def hamiltonian_cycle_bruteforce(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    if n <= 2:
        return False
    if n == 3:
        # triangle required
        return all(frozenset([i, (i+1)%3]) in edges for i in range(3))
    # try all permutations starting with 0 to avoid cycles rotations
    verts = list(range(n))
    for perm in itertools.permutations(verts[1:]):
        cycle = (0, ) + perm
        ok = True
        for i in range(n):
            u = cycle[i]
            v = cycle[(i+1)%n]
            if frozenset([u, v]) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause => unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    # no clauses => sat
    for bits in range(1 << m):
        assign = [(bits >> i) & 1 == 1 for i in range(m)]  # index 0 => var1
        ok = True
        for clause in clauses:
            sat_clause = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    sat_clause = True
                    break
            if not sat_clause:
                ok = False
                break
        if ok:
            return True
    return False


def random_graph(max_n=4, edge_prob=0.5):
    # Keep n small (<=4) to keep SAT brute‑force tractable.
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        inst = random_graph()
        # validate
        HamiltonianCycle.validate(inst)
        reduced = reduce(inst)
        Sat.validate(reduced)
        ans1 = hamiltonian_cycle_bruteforce(inst)
        ans2 = sat_bruteforce(reduced)
        if ans1 == ans2:
            passed += 1
        else:
            print('Mismatch!')
            print('Instance:', json.dumps(inst))
            print('Reduced:', json.dumps(reduced))
            print('HC answer', ans1, 'SAT answer', ans2)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests()
    print(f"Passed {passed}/{total} tests")
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written to verdict.json')
