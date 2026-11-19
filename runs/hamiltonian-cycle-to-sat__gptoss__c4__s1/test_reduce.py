import itertools
import json
from problems import HamiltonianCycle, Sat
from reduce import reduce

def hc_bruteforce(instance):
    n = instance['n']
    edges = set()
    for u,v in instance['edges']:
        edges.add((u,v))
        edges.add((v,u))
    if n <= 2:
        return False
    # generate permutations of vertices starting at 0 to avoid cycles rotations
    verts = list(range(n))
    for perm in itertools.permutations(verts[1:]):
        cycle = (0,)+perm
        ok = True
        for i in range(n):
            a = cycle[i]
            b = cycle[(i+1)%n]
            if (a,b) not in edges:
                ok=False
                break
        if ok:
            return True
    return False

def sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    # empty clause makes unsat immediately
    for clause in clauses:
        if len(clause)==0:
            return False
    for assign in itertools.product([False, True], repeat=m):
        good = True
        for clause in clauses:
            clause_val = False
            for lit in clause:
                var = abs(lit)-1
                val = assign[var]
                if lit>0 and val:
                    clause_val=True
                if lit<0 and not val:
                    clause_val=True
                if clause_val:
                    break
            if not clause_val:
                good=False
                break
        if good:
            return True
    return False

def test_all_graphs(max_n=4):
    total=0; passed=0
    for n in range(max_n+1):
        # generate all possible edge sets without duplicates
        possible_edges = [(u,v) for u in range(n) for v in range(u+1,n)]
        for r in range(len(possible_edges)+1):
            for edges in itertools.combinations(possible_edges, r):
                # format as list of [u,v]
                instance = {'n': n, 'edges': [list(e) for e in edges]}
                # validate
                HamiltonianCycle.validate(instance)
                hc = hc_bruteforce(instance)
                sat_inst = reduce(instance)
                # validate sat instance
                Sat.validate(sat_inst)
                sat = sat_bruteforce(sat_inst)
                if hc==sat:
                    passed+=1
                else:
                    print('Mismatch', instance, hc, sat)
                total+=1
    print('tested', total, 'instances, passed', passed)
    return total, passed

if __name__=='__main__':
    total, passed = test_all_graphs(4)
    # write verdict
    verdict = {
        "verified": total==passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json','w') as f:
        json.dump(verdict, f)
    print('verdict', verdict)
