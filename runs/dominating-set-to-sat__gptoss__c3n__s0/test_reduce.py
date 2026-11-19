import random
import itertools
import sys
from problems import DominatingSet, Sat
from reduce import reduce


def dominating_set_bruteforce(instance):
    DominatingSet.validate(instance)
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    if n == 0:
        return True
    # build adjacency set
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # check all subsets up to size k
    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            D = set(subset)
            # verify domination
            ok = True
            for v in range(n):
                if v not in D and not (adj[v] & D):
                    ok = False
                    break
            if ok:
                return True
    return False


def sat_bruteforce(instance):
    Sat.validate(instance)
    m = instance['num_vars']
    clauses = instance['clauses']
    # if any empty clause -> unsat
    for cl in clauses:
        if len(cl) == 0:
            return False
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]  # var i -> assignment[i]
        satisfied = True
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
                satisfied = False
                break
        if satisfied:
            return True
    return False


def random_instance(max_n=5):
    n = random.randint(0, max_n)
    # generate all possible edges without duplicates
    possible = [(u, v) for u in range(n) for v in range(u+1, n)]
    edges = []
    for u, v in possible:
        if random.choice([True, False]):
            edges.append([u, v])
    k = random.randint(-1, n+1)
    return {"n": n, "edges": edges, "k": k}


def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_instance()
        ds_ans = dominating_set_bruteforce(inst)
        sat_inst = reduce(inst)
        sat_ans = sat_bruteforce(sat_inst)
        total += 1
        if ds_ans == sat_ans:
            passed += 1
        else:
            print('FAIL')
            print('Instance:', inst)
            print('Reduced:', sat_inst)
            print('DomSet:', ds_ans, 'SAT:', sat_ans)
            sys.exit(1)
    print(f'All {passed}/{total} tests passed')

if __name__ == '__main__':
    main()
