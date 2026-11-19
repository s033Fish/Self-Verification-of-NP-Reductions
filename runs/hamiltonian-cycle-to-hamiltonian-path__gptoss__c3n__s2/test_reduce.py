import itertools
import unittest
from typing import List, Dict, Any

from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce


def solve_hamiltonian_cycle(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n <= 2:
        return False
    # generate permutations fixing first vertex to reduce symmetry
    vertices = list(range(n))
    for perm in itertools.permutations(vertices[1:]):
        path = (vertices[0],) + perm
        # check edges between consecutive and last to first
        ok = True
        for i in range(n):
            a = path[i]
            b = path[(i + 1) % n]
            if frozenset((a, b)) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def solve_hamiltonian_path(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        return frozenset((0, 1)) in edges
    vertices = list(range(n))
    for perm in itertools.permutations(vertices):
        ok = True
        for i in range(n - 1):
            a = perm[i]
            b = perm[i + 1]
            if frozenset((a, b)) not in edges:
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
        edges: List[List[int]] = []
        for idx, (u, v) in enumerate(possible_edges):
            if mask & (1 << idx):
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs


class TestReduction(unittest.TestCase):
    def test_all_small_graphs(self):
        for n in range(0, 6):
            for g in all_graphs(n):
                # validate instances (should be valid by construction)
                HamiltonianCycle.validate(g)
                hc = solve_hamiltonian_cycle(g)
                reduced = reduce(g)
                HamiltonianPath.validate(reduced)
                hp = solve_hamiltonian_path(reduced)
                self.assertEqual(hc, hp, f"Mismatch on n={n}, edges={g['edges']}")

if __name__ == "__main__":
    unittest.main()
