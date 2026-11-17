import itertools
import json
import sys
from typing import List, Dict, Any

import problems
from reduce import reduce


def solve_hamiltonian_path(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n == 0:
        return False
    if n == 1:
        return True
    if n == 2:
        # For two vertices, a Hamiltonian path exists iff the single possible edge is present.
        return frozenset((0, 1)) in edges
    # brute-force permutations
    for perm in itertools.permutations(range(n)):
        ok = True
        for i in range(n - 1):
            if frozenset((perm[i], perm[i + 1])) not in edges:
                ok = False
                break
        if ok:
            return True
    return False


def solve_hamiltonian_cycle(instance: Dict[str, Any]) -> bool:
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    if n <= 2:
        return False
    if n == 3:
        # triangle required
        required = {frozenset((0,1)), frozenset((1,2)), frozenset((2,0))}
        return required.issubset(edges)
    # brute-force permutations fixing start at 0 to avoid cycles rotations
    for perm in itertools.permutations(range(1, n)):
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


def all_graphs(n: int) -> List[Dict[str, Any]]:
    possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    graphs = []
    for mask in range(1 << len(possible_edges)):
        edges = []
        for idx, (u, v) in enumerate(possible_edges):
            if mask & (1 << idx):
                edges.append([u, v])
        graphs.append({"n": n, "edges": edges})
    return graphs


def main():
    total = 0
    passed = 0
    for n in range(0, 6):  # up to 5 vertices
        for g in all_graphs(n):
            problems.HamiltonianPath.validate(g)
            src_ans = solve_hamiltonian_path(g)
            red = reduce(g)
            problems.HamiltonianCycle.validate(red)
            tgt_ans = solve_hamiltonian_cycle(red)
            total += 1
            if src_ans == tgt_ans:
                passed += 1
            else:
                print("Mismatch! n=", n, "graph=", g, "src=", src_ans, "tgt=", tgt_ans, file=sys.stderr)
                sys.exit(1)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
