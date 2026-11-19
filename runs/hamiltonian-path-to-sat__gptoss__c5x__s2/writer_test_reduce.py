import itertools
import random
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
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n - 1):
            if frozenset((perm[i], perm[i + 1])) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # empty clause -> unsat
    for clause in clauses:
        if len(clause) == 0:
            return False
    # brute‑force all assignments (m <= 16 in our tests)
    for bits in range(1 << m):
        assignment = [(bits >> i) & 1 == 1 for i in range(m)]
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def generate_all_graphs(n: int) -> List[Dict[str, Any]]:
    vertices = list(range(n))
    possible_edges = list(itertools.combinations(vertices, 2))
    graphs = []
    for mask in range(1 << len(possible_edges)):
        edges = []
        for i, e in enumerate(possible_edges):
            if (mask >> i) & 1:
                edges.append([e[0], e[1]])
        graphs.append({"n": n, "edges": edges})
    return graphs


def main():
    total = 0
    passed = 0
    # Exhaustive testing for n up to 4 (num_vars <= 16)
    for n in range(0, 5):
        for g in generate_all_graphs(n):
            total += 1
            hp = solve_hamiltonian(g)
            sat_instance = reduce(g)
            Sat.validate(sat_instance)
            sat = solve_sat(sat_instance)
            if hp == sat:
                passed += 1
            else:
                print("Mismatch! n=", n, "graph=", g, "hp=", hp, "sat=", sat)
                sys.exit(1)
    # Random testing for small graphs (n <= 4)
    for _ in range(200):
        n = random.randint(0, 4)
        edges = []
        for u in range(n):
            for v in range(u + 1, n):
                if random.choice([True, False]):
                    edges.append([u, v])
        g = {"n": n, "edges": edges}
        total += 1
        hp = solve_hamiltonian(g)
        sat_instance = reduce(g)
        Sat.validate(sat_instance)
        sat = solve_sat(sat_instance)
        if hp == sat:
            passed += 1
        else:
            print("Random mismatch!", g, hp, sat)
            sys.exit(1)
    print(f"All tests passed: {passed}/{total}")
    import json
    with open('verdict.json', 'w') as f:
        json.dump({"verified": True, "tests_run": total, "tests_passed": passed}, f)

if __name__ == "__main__":
    main()
