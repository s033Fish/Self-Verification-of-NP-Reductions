"""Test suite for the reduction from 3-Coloring to 1-in-3 SAT.

The repository provides a ``reduce`` function that maps a ThreeColoring
instance to a OneInThreeSat instance.  To verify its correctness we
implement brute‑force solvers for both problems and check that the
answer of the target instance matches the answer of the source instance
for a wide range of small graphs.

The tests enumerate all graphs with up to ``MAX_N`` vertices (including
the empty graph) and all possible edge subsets.  For each graph we:

1. Validate the source instance using ``ThreeColoring.validate``.
2. Compute the expected answer with ``solve_three_coloring``.
3. Reduce the instance with ``reduce``.
4. Validate the produced target instance with ``OneInThreeSat.validate``.
5. Compute the answer for the target with ``solve_one_in_three_sat``.
6. Assert that both answers are identical.

If all generated instances satisfy the equivalence, the reduction is
considered verified.
"""

from itertools import combinations, product
from typing import List, Dict

from problems import ThreeColoring, OneInThreeSat
from reduce import reduce as reduce_instance


def solve_three_coloring(instance: Dict) -> bool:
    """Brute‑force solver for 3‑Coloring.

    Returns ``True`` iff the graph can be coloured with three colours
    such that adjacent vertices receive different colours.
    """
    n = instance["n"]
    edges: List[List[int]] = instance["edges"]
    for coloring in product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def solve_one_in_three_sat(instance: Dict) -> bool:
    """Brute‑force solver for positive 1‑in‑3 SAT.

    Returns ``True`` iff there exists an assignment to the ``num_vars``
    variables such that exactly one literal in each clause is true.
    """
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    # iterate over all possible truth assignments (True/False) for m vars
    for assignment in product([False, True], repeat=m):
        good = True
        for clause in clauses:
            # clause literals are all positive, so we just look at the variable
            true_count = sum(assignment[var - 1] for var in clause)
            if true_count != 1:
                good = False
                break
        if good:
            return True
    return False


def generate_all_graphs(max_n: int):
    """Yield all valid ThreeColoring instances with ``n`` up to ``max_n``.

    For each ``n`` we consider every possible subset of the
    ``n*(n-1)/2`` undirected edges.  The instance dictionary follows the
    format required by ``ThreeColoring``.
    """
    for n in range(max_n + 1):
        # list of all unordered pairs (u, v) with u < v
        all_pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for r in range(len(all_pairs) + 1):
            for edges in combinations(all_pairs, r):
                # convert to list-of-lists as required
                yield {"n": n, "edges": [list(e) for e in edges]}


def main() -> None:
    MAX_N = 5  # small enough for exhaustive enumeration
    total = 0
    passed = 0
    for src in generate_all_graphs(MAX_N):
        total += 1
        # Validate source instance (should never raise)
        ThreeColoring.validate(src)
        src_ans = solve_three_coloring(src)
        tgt = reduce_instance(src)
        # Validate target instance
        OneInThreeSat.validate(tgt)
        tgt_ans = solve_one_in_three_sat(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", src, src_ans, tgt, tgt_ans)
            break
    # Write verdict file
    import json
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f)
    # Also print for visibility
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()

