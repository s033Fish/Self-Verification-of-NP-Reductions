import random
import itertools
import sys
from problems import ThreeColoring, Sat
from reduce import reduce

def three_coloring_bruteforce(instance):
    n = instance["n"]
    edges = instance["edges"]
    # assign colors 0,1,2
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False

def sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assignment in itertools.product([False, True], repeat=m):
        # assignment is tuple indexed 0..m-1 for var 1..m
        all_sat = True
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
                all_sat = False
                break
        if all_sat:
            return True
    return False

def test_random(num_tests=200):
    for _ in range(num_tests):
        n = random.randint(0,5)
        # generate possible edges without duplicates
        possible = [(i,j) for i in range(n) for j in range(i+1,n)]
        edges = []
        for (i,j) in possible:
            if random.random() < 0.3:
                edges.append([i,j])
        instance = {"n": n, "edges": edges}
        ThreeColoring.validate(instance)
        # compute answers
        ans_src = three_coloring_bruteforce(instance)
        red = reduce(instance)
        Sat.validate(red)
        ans_tgt = sat_bruteforce(red)
        if ans_src != ans_tgt:
            print("Mismatch!", instance, red, ans_src, ans_tgt)
            return False
    return True

def test_edge_cases():
    # empty graph
    inst = {"n":0, "edges":[]}
    assert three_coloring_bruteforce(inst)
    red = reduce(inst)
    assert sat_bruteforce(red)
    # K4 (no)
    n=4
    edges=[[i,j] for i in range(n) for j in range(i+1,n)]
    inst={"n":4,"edges":edges}
    assert not three_coloring_bruteforce(inst)
    red=reduce(inst)
    assert not sat_bruteforce(red)
    # triangle (yes)
    inst={"n":3,"edges":[[0,1],[1,2],[0,2]]}
    assert three_coloring_bruteforce(inst)
    red=reduce(inst)
    assert sat_bruteforce(red)
    return True

if __name__ == "__main__":
    ok = test_random() and test_edge_cases()
    print("All tests passed" if ok else "Tests failed")
    sys.exit(0 if ok else 1)
