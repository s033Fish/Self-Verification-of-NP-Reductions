import itertools
import json
import sys
from typing import List, Dict, Any

from problems import HamiltonianPath, Sat
from reduce import reduce


def solve_hamiltonian(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n == 0:
        return False
    if n == 1:
        return True
    # generate all permutations
    for perm in itertools.permutations(range(n)):
        ok = True
        for a, b in zip(perm, perm[1:]):
            if frozenset((a, b)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # early unsat if empty clause
    for cl in clauses:
        if len(cl) == 0:
            return False
    for assign in range(1 << m):
        # assignment: bit i -> variable i+1 true if 1
        ok = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = (assign >> var) & 1
                if lit > 0 and val == 1:
                    clause_sat = True
                    break
                if lit < 0 and val == 0:
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False


def all_graphs(n: int) -> List[Dict[str, Any]]:
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
    for n in range(0, 5):  # up to 4 vertices
        for instance in all_graphs(n):
            total += 1
            # validate instances
            HamiltonianPath.validate(instance)
            src_ans = solve_hamiltonian(instance)
            red = reduce(instance)
            Sat.validate(red)
            tgt_ans = solve_sat(red)
            if src_ans == tgt_ans:
                passed += 1
            else:
                print("Mismatch!", instance, src_ans, tgt_ans, file=sys.stderr)
                sys.exit(1)
    # also test n=2 edge cases explicitly
    # generate all possible edges for n=2 (already covered)
    print(json.dumps({"verified": True, "tests_run": total, "tests_passed": passed}))

if __name__ == "__main__":
    main()
