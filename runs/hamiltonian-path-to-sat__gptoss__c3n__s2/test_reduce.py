import itertools
import json
import sys
from problems import HamiltonianPath, Sat
from reduce import reduce

def hamiltonian_path_bruteforce(instance):
    n = instance['n']
    edges = set(frozenset(e) for e in instance['edges'])
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset((0,1)) in edges
    verts = list(range(n))
    for perm in itertools.permutations(verts):
        ok = True
        for i in range(n-1):
            if frozenset((perm[i], perm[i+1])) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # quick check for empty clause -> unsat
    for cl in clauses:
        if len(cl) == 0:
            return False
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # index 0 -> var1
        good = True
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
                good = False
                break
        if good:
            return True
    return False

def run_tests():
    total = 0
    passed = 0
    # test all graphs up to n=4
    for n in range(0,5):
        vertices = list(range(n))
        possible_edges = list(itertools.combinations(vertices,2))
        for edge_mask in range(1 << len(possible_edges)):
            edges = []
            for i, e in enumerate(possible_edges):
                if (edge_mask >> i) & 1:
                    edges.append([e[0], e[1]])
            instance = {'n': n, 'edges': edges}
            # validate
            HamiltonianPath.validate(instance)
            hp = hamiltonian_path_bruteforce(instance)
            sat_instance = reduce(instance)
            Sat.validate(sat_instance)
            sat_res = sat_bruteforce(sat_instance)
            total += 1
            if hp == sat_res:
                passed += 1
            else:
                print('Mismatch', instance, hp, sat_res)
                sys.exit(1)
    print('Tests run', total, 'passed', passed)
    return total, passed

if __name__ == '__main__':
    total, passed = run_tests()
    verdict = {'verified': total==passed, 'tests_run': total, 'tests_passed': passed}
    with open('verdict.json','w') as f:
        json.dump(verdict, f)
    print('Verdict written to verdict.json')
