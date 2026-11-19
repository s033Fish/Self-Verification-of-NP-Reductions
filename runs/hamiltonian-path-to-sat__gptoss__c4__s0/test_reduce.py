import itertools
import random
import json
from problems import HamiltonianPath, Sat
from reduce import reduce

def solve_hamiltonian(instance):
    n = instance["n"]
    edges = {frozenset(e) for e in instance["edges"]}
    if n == 0:
        return False
    if n == 1:
        return True
    # generate all permutations of vertices
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n-1):
            if frozenset((perm[i], perm[i+1])) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

def solve_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # if any empty clause -> unsat
    for c in clauses:
        if len(c) == 0:
            return False
    for bits in itertools.product([False, True], repeat=m):
        assignment = {i+1: bits[i] for i in range(m)}
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit)
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

# generate random small instances and test
random.seed(0)
tests = 0
passed = 0
for n in range(0,5):
    # generate all possible edge subsets for small n (limit)
    vertices = list(range(n))
    possible_edges = []
    for u in range(n):
        for v in range(u+1, n):
            possible_edges.append([u,v])
    # iterate over some subsets
    for mask in range(1 << len(possible_edges)):
        edges = [possible_edges[i] for i in range(len(possible_edges)) if (mask>>i)&1]
        instance = {"n": n, "edges": edges}
        # validate
        HamiltonianPath.validate(instance)
        # solve source
        src_ans = solve_hamiltonian(instance)
        # reduce
        sat_inst = reduce(instance)
        Sat.validate(sat_inst)
        tgt_ans = solve_sat(sat_inst)
        tests += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", instance, src_ans, tgt_ans)
            raise SystemExit(1)
print("All tests passed", tests, passed)
