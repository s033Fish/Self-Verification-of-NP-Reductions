import itertools
import json
import sys
from problems import HamiltonianCycle, Sat
from reduce import reduce

# Brute-force Hamiltonian cycle solver

def has_hamiltonian_cycle(instance):
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n <= 2:
        return False
    vertices = list(range(n))
    for perm in itertools.permutations(vertices[1:]):
        cycle = (0,) + perm
        ok = True
        for i in range(n):
            u = cycle[i]
            v = cycle[(i+1)%n]
            if frozenset((u, v)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False

# Brute-force SAT solver

def is_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for c in clauses:
        if len(c) == 0:
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


def test_all_graphs(max_n=5):
    total = 0
    passed = 0
    for n in range(max_n+1):
        vertices = list(range(n))
        possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for edge_mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if (edge_mask >> i) & 1:
                    edges.append([u, v])
            instance = {"n": n, "edges": edges}
            HamiltonianCycle.validate(instance)
            hc = has_hamiltonian_cycle(instance)
            sat_instance = reduce(instance)
            Sat.validate(sat_instance)
            sat = is_sat(sat_instance)
            total += 1
            if hc == sat:
                passed += 1
            else:
                print("Mismatch! n=", n, "edges=", edges, "hc=", hc, "sat=", sat)
                sys.exit(1)
    print(f"All {total} instances passed.")
    return total, passed

if __name__ == "__main__":
    # Use n up to 4 to keep runtime reasonable.
    total, passed = test_all_graphs(4)
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
