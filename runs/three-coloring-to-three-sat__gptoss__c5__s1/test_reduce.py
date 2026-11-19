"""Automated tests for the reduction from ThreeColoring to ThreeSat.

The script implements brute‑force solvers for both source and target
problems and checks that for a large collection of small instances the
answer of the reduction matches the original answer.

If all tests pass, ``verified`` is set to ``true`` in ``verdict.json``.
Otherwise it is ``false`` and the failing instance is printed for
debugging.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

from problems import ThreeColoring, ThreeSat
from reduce import reduce as reduce_instance


def solve_three_coloring(instance: dict) -> bool:
    """Brute‑force solver for 3‑Coloring.

    Returns ``True`` iff the graph is 3‑colorable.
    """
    ThreeColoring.validate(instance)
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    # each vertex colour in {0,1,2}
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_sat(instance: dict) -> bool:
    """Brute‑force solver for 3‑SAT.

    Returns ``True`` iff the formula is satisfiable.
    """
    ThreeSat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assignment in itertools.product([False, True], repeat=m):
        # assignment indexed from 0 -> variable 1
        ok = True
        for clause in clauses:
            clause_val = False
            for lit in clause:
                var = abs(lit) - 1
                lit_val = assignment[var]
                if lit < 0:
                    lit_val = not lit_val
                if lit_val:
                    clause_val = True
                    break
            if not clause_val:
                ok = False
                break
        if ok:
            return True
    return False


def generate_graph_instances(max_n: int = 3):
    """Yield all valid ThreeColoring instances with up to ``max_n`` vertices.

    For each ``n`` we enumerate all subsets of the possible undirected
    edges.  The total number of instances stays manageable for ``max_n``
    up to five (10 possible edges → 1024 subsets).
    """
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = [(i, j) for i in vertices for j in vertices if i < j]
        for edge_subset in itertools.product([0, 1], repeat=len(possible_edges)):
            edges = [list(e) for include, e in zip(edge_subset, possible_edges) if include]
            yield {"n": n, "edges": edges}


def main() -> None:
    total = 0
    passed = 0
    for instance in generate_graph_instances():
        total += 1
        try:
            src_ans = solve_three_coloring(instance)
            reduced = reduce_instance(instance)
            tgt_ans = solve_three_sat(reduced)
            if src_ans == tgt_ans:
                passed += 1
            else:
                print("FAILURE on instance:")
                print(json.dumps(instance, indent=2))
                print("source answer:", src_ans)
                print("reduced instance:", json.dumps(reduced, indent=2))
                print("target answer:", tgt_ans)
                break
        except Exception as e:
            print("Exception during testing:", e)
            break

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    if not verdict["verified"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
