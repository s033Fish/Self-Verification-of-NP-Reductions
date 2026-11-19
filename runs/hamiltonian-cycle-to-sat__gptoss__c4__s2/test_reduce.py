import itertools
import json
import sys
from problems import HamiltonianCycle, Sat, InvalidInstance
from reduce import reduce

def solve_hamiltonian(instance):
    n = instance['n']
    edges = set()
    for u, v in instance['edges']:
        edges.add((u, v))
        edges.add((v, u))
    if n <= 2:
        return False
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n):
            u = perm[i]
            v = perm[(i+1)%n]
            if (u, v) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def solve_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause means unsat
    for assignment in itertools.product([False, True], repeat=m):
        sat = True
        for clause in clauses:
            # empty clause is always false
            if len(clause) == 0:
                sat = False
                break
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

def generate_graphs(max_n=4):
    for n in range(0, max_n+1):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for r in range(len(possible_edges)+1):
            for edges in itertools.combinations(possible_edges, r):
                # edges list as required format
                yield {'n': n, 'edges': [list(e) for e in edges]}

def main():
    total = 0
    passed = 0
    for g in generate_graphs(4):
        try:
            HamiltonianCycle.validate(g)
        except InvalidInstance as e:
            print('Invalid generated instance', g, e)
            continue
        hc = solve_hamiltonian(g)
        sat_inst = reduce(g)
        sat_ans = solve_sat(sat_inst)
        total += 1
        if hc == sat_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('Graph:', json.dumps(g))
            print('Hamiltonian:', hc)
            print('SAT instance:', json.dumps(sat_inst)[:200])
            print('SAT answer:', sat_ans)
            sys.exit(1)
    print('All tests passed', passed, '/', total)
    # write verdict
    verdict = {'verified': True, 'tests_run': total, 'tests_passed': passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
