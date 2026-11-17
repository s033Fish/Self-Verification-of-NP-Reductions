import itertools
import random
import json
import sys
from pathlib import Path

import reduce
from problems import ThreeColoring, OneInThreeSat


def three_coloring_bruteforce(instance):
    n = instance["n"]
    edges = instance["edges"]
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def one_in_three_sat_solver(instance):
    """Simple backtracking solver for 1‑in‑3‑SAT with propagation."""
    m = instance["num_vars"]
    clauses = [list(c) for c in instance["clauses"]]
    assign: list[bool | None] = [None] * (m + 1)  # 1‑based

    def propagate() -> bool:
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                vals = [assign[abs(lit)] for lit in clause]
                true_cnt = sum(1 for v in vals if v is True)
                false_cnt = sum(1 for v in vals if v is False)
                if true_cnt > 1:
                    return False
                if true_cnt == 1:
                    for lit, v in zip(clause, vals):
                        if v is None:
                            assign[abs(lit)] = False
                            changed = True
                elif false_cnt == 2:
                    for lit, v in zip(clause, vals):
                        if v is None:
                            assign[abs(lit)] = True
                            changed = True
                elif false_cnt == 3:
                    return False
        return True

    def backtrack() -> bool:
        if not propagate():
            return False
        # find unassigned
        try:
            var = next(i for i, v in enumerate(assign[1:], start=1) if v is None)
        except StopIteration:
            return all(sum(assign[abs(lit)] for lit in clause) == 1 for clause in clauses)
        saved = assign.copy()
        for val in (False, True):
            assign[var] = val
            if backtrack():
                return True
            assign[:] = saved
        return False

    return backtrack()


def generate_random_graph(n, edge_prob=0.5):
    edges = []
    for u in range(n):
        for v in range(u+1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main():
    random.seed(0)
    total = 0
    passed = 0
    for n in range(0, 5):
        verts = list(range(n))
        possible_edges = [(u, v) for u in verts for v in verts if u < v]
        for mask in range(1 << len(possible_edges)):
            edges = []
            for i, (u, v) in enumerate(possible_edges):
                if mask & (1 << i):
                    edges.append([u, v])
            instance = {"n": n, "edges": edges}
            ThreeColoring.validate(instance)
            ans_src = three_coloring_bruteforce(instance)
            red = reduce.reduce(instance)
            OneInThreeSat.validate(red)
            ans_tgt = one_in_three_sat_solver(red)
            total += 1
            if ans_src == ans_tgt:
                passed += 1
            else:
                print("Mismatch!", instance, red)
                sys.exit(1)
    print(f"All {total} tests passed: {passed}/{total}")
    verdict = {"verified": True, "tests_run": total, "tests_passed": passed}
    Path('verdict.json').write_text(json.dumps(verdict))

if __name__ == "__main__":
    main()
