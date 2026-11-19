import itertools
import json
import sys
from typing import Dict, List

from hamiltonian_solver import is_hamiltonian
from sat_solver import is_sat
from reduce import reduce


def all_graphs(n: int):
    vertices = list(range(n))
    possible_edges = [(u, v) for u in vertices for v in vertices if u < v]
    for mask in range(1 << len(possible_edges)):
        edges = []
        for i, (u, v) in enumerate(possible_edges):
            if mask & (1 << i):
                edges.append([u, v])
        yield {"n": n, "edges": edges}


def run_tests(max_n: int = 5):
    total = 0
    passed = 0
    for n in range(max_n + 1):
        for g in all_graphs(n):
            total += 1
            ham = is_hamiltonian(g)
            sat_instance = reduce(g)
            sat = is_sat(sat_instance)
            if ham == sat:
                passed += 1
            else:
                print("Mismatch!", g, "ham", ham, "sat", sat, file=sys.stderr)
                return total, passed, False
    return total, passed, True

if __name__ == "__main__":
    # Use n up to 4 for reasonable runtime
    total, passed, ok = run_tests(4)
    verdict = {"verified": ok, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
    sys.exit(0 if ok else 1)
