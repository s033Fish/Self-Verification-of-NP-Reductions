import itertools
import json
import os
from typing import List, Dict, Any

from problems import HamiltonianCycle, Sat
from reduce import reduce


def solve_hamiltonian(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n <= 2:
        return False
    if n == 3:
        # triangle only
        return all(frozenset({i, j}) in edges for i, j in [(0,1),(1,2),(0,2)])
    # brute force permutations of vertices as cycle starting at 0 to avoid rotations
    verts = list(range(n))
    for perm in itertools.permutations(verts[1:]):
        cycle = (0,) + perm
        ok = True
        for i in range(n):
            u = cycle[i]
            v = cycle[(i+1)%n]
            if frozenset({u, v}) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # empty clause -> unsat immediately
    for cl in clauses:
        if len(cl) == 0:
            return False
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def all_graphs(n: int) -> List[Dict[str, Any]]:
    verts = list(range(n))
    possible_edges = [(i, j) for i in verts for j in verts if i < j]
    graphs = []
    for mask in range(1 << len(possible_edges)):
        edges = []
        for idx, (u, v) in enumerate(possible_edges):
            if mask & (1 << idx):
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs


def run_tests() -> Dict[str, int]:
    total = 0
    passed = 0
    for n in range(0, 5):
        for g in all_graphs(n):
            total += 1
            # validate input
            HamiltonianCycle.validate(g)
            hc = solve_hamiltonian(g)
            sat_inst = reduce(g)
            # validate output
            Sat.validate(sat_inst)
            sat_res = solve_sat(sat_inst)
            if hc == sat_res:
                passed += 1
            else:
                print("Mismatch! n=", n, "graph=", g, "hc=", hc, "sat=", sat_res)
    return {"total": total, "passed": passed}

if __name__ == "__main__":
    results = run_tests()
    verified = results["passed"] == results["total"]
    verdict = {
        "verified": verified,
        "tests_run": results["total"],
        "tests_passed": results["passed"],
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))
