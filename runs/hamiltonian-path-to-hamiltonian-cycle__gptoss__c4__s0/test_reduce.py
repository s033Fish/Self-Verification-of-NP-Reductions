import itertools
import json
import random
import sys
from typing import List, Dict, Any

from reduce import reduce as reduce_instance
from problems import HamiltonianPath, HamiltonianCycle


def is_edge_in(edges_set, u, v):
    return (u, v) in edges_set or (v, u) in edges_set


def solve_hamiltonian_path(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    if n == 0:
        return False
    if n == 1:
        return True
    edge_set = {tuple(e) for e in edges}
    # generate all permutations of vertices
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n - 1):
            if not is_edge_in(edge_set, perm[i], perm[i+1]):
                ok = False
                break
        if ok:
            return True
    return False


def solve_hamiltonian_cycle(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    if n <= 2:
        return False
    edge_set = {tuple(e) for e in edges}
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n):
            u = perm[i]
            v = perm[(i+1)%n]
            if not is_edge_in(edge_set, u, v):
                ok = False
                break
        if ok:
            return True
    return False


def random_graph(n: int, p: float = 0.5) -> Dict[str, Any]:
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def test_random(num_cases: int = 200):
    for _ in range(num_cases):
        n = random.randint(0, 6)
        g = random_graph(n, p=0.4)
        # validate source and target
        HamiltonianPath.validate(g)
        # compute answers
        ans_path = solve_hamiltonian_path(g)
        g_red = reduce_instance(g)
        HamiltonianCycle.validate(g_red)
        ans_cycle = solve_hamiltonian_cycle(g_red)
        if ans_path != ans_cycle:
            print("Mismatch!", g, g_red, ans_path, ans_cycle)
            return False
    return True

if __name__ == "__main__":
    ok = test_random(500)
    result = {"verified": ok, "tests_run": 500, "tests_passed": 500 if ok else 0}
    print(json.dumps(result))
    sys.exit(0 if ok else 1)
