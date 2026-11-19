import itertools
import json
import sys
from problems import HamiltonianPath, Sat
from reduce import reduce

def hp_bruteforce(instance):
    n = instance['n']
    edges = set()
    for u, v in instance['edges']:
        edges.add((u, v))
        edges.add((v, u))
    if n == 0:
        return False
    if n == 1:
        return True
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n-1):
            if (perm[i], perm[i+1]) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause -> unsatisfiable
    for clause in clauses:
        if len(clause) == 0:
            return False
    # no clauses -> satisfiable
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # index 0 -> var 1
        good = True
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
                good = False
                break
        if good:
            return True
    return False

def generate_graphs(n):
    vertices = list(range(n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    for mask in range(1 << len(possible_edges)):
        edges = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        yield {'n': n, 'edges': edges}


def main():
    total = 0
    passed = 0
    for n in range(0, 5):
        for g in generate_graphs(n):
            total += 1
            hp = hp_bruteforce(g)
            sat_inst = reduce(g)
            # validate target instance
            Sat.validate(sat_inst)
            sat = sat_bruteforce(sat_inst)
            if hp == sat:
                passed += 1
            else:
                print('Mismatch for graph:', g)
                print('HP:', hp, 'SAT:', sat)
                print('SAT instance:', sat_inst)
                sys.exit(1)
    print(f'Tested {total} instances, all passed.')
    # write verdict
    verdict = {'verified': True, 'tests_run': total, 'tests_passed': passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
