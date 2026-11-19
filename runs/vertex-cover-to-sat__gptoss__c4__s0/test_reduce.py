import itertools
import random
import json
from problems import VertexCover, Sat
from reduce import reduce

def vc_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    k = instance['k']
    if k < 0:
        return False
    # enumerate subsets up to size k
    vertices = list(range(n))
    for r in range(k+1):
        for subset in itertools.combinations(vertices, r):
            cover = set(subset)
            ok = True
            for u,v in edges:
                if u not in cover and v not in cover:
                    ok = False
                    break
            if ok:
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
        assign = {i+1: bits[i] for i in range(m)}
        all_ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit)
                val = assign[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                all_ok = False
                break
        if all_ok:
            return True
    return False


def generate_all_graphs(max_n=4):
    graphs = []
    for n in range(max_n+1):
        vertices = list(range(n))
        possible_edges = [(i,j) for i in vertices for j in vertices if i<j]
        for edges_mask in range(1<<len(possible_edges)):
            edges = []
            for idx, (u,v) in enumerate(possible_edges):
                if edges_mask & (1<<idx):
                    edges.append([u,v])
            for k in range(-1, n+2):
                graphs.append({'n': n, 'edges': edges, 'k': k})
    return graphs


def main():
    tests = 0
    passed = 0
    for instance in generate_all_graphs(4):
        # validate source
        VertexCover.validate(instance)
        vc_ans = vc_bruteforce(instance)
        sat_instance = reduce(instance)
        Sat.validate(sat_instance)
        sat_ans = sat_bruteforce(sat_instance)
        tests += 1
        if vc_ans == sat_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('VC instance', instance)
            print('VC answer', vc_ans)
            print('SAT instance', sat_instance)
            print('SAT answer', sat_ans)
            break
    verdict = {
        "verified": passed == tests,
        "tests_run": tests,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == '__main__':
    main()
