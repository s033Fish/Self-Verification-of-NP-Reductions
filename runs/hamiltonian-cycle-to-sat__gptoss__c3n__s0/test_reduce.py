import itertools
import json
import sys
from typing import List, Dict

import reduce as red
from problems import HamiltonianCycle, Sat

# Brute-force Hamiltonian Cycle solver
def hamiltonian_cycle_bruteforce(instance: Dict) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n <= 2:
        return False
    verts = list(range(n))
    for perm in itertools.permutations(verts[1:]):
        cycle = (0,) + perm
        ok = True
        for i in range(n):
            u = cycle[i]
            v = cycle[(i + 1) % n]
            if frozenset((u, v)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

# Brute-force SAT solver
def sat_bruteforce(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for clause in clauses:
        if len(clause) == 0:
            return False
    for assignment in range(1 << m):
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = bool((assignment >> var) & 1)
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False

def all_graphs(n: int) -> List[Dict]:
    verts = list(range(n))
    possible_edges = [(u, v) for u in verts for v in verts if u < v]
    graphs = []
    for mask in range(1 << len(possible_edges)):
        edges = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs

def main():
    total = 0
    passed = 0
    for n in range(0, 5):  # up to 4 vertices, exhaustive
        for g in all_graphs(n):
            total += 1
            HamiltonianCycle.validate(g)
            src_yes = hamiltonian_cycle_bruteforce(g)
            red_inst = red.reduce(g)
            Sat.validate(red_inst)
            tgt_yes = sat_bruteforce(red_inst)
            if src_yes == tgt_yes:
                passed += 1
            else:
                print("Mismatch! n=", n, "graph=", g, file=sys.stderr)
                print("src_yes=", src_yes, "tgt_yes=", tgt_yes, file=sys.stderr)
                sys.exit(1)
    # No additional random tests to keep SAT brute-force tractable.
    print(f"All tests passed: {passed}/{total}")
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
