"""Test the reduction from VertexCover to IndependentSet.

The test enumerates all small graphs (up to 5 vertices) and a range of k
values, checks that the instances are valid according to the problem
definitions, runs the reduction, and verifies that the yes/no answer of the
source instance matches that of the reduced target instance.

The script prints a JSON object with the number of tests run, how many
passed, and whether the reduction is verified.  It exits with status 0 if
all tests pass, otherwise with status 1.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Tuple

import problems  # provides VertexCover and IndependentSet classes
import reduce


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has a vertex cover of size at most k.

    Brute‑force enumeration of subsets is feasible for the tiny graphs used
    in the tests (n ≤ 5).
    """
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]
    if k < 0:
        return False
    # any subset of size ≤ k that touches every edge
    for r in range(k + 1):
        for subset in itertools.combinations(range(n), r):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def independent_set_bruteforce(instance: dict) -> bool:
    """Return True iff the graph has an independent set of size at least k."""
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    # check all subsets of size >= k
    for r in range(k, n + 1):
        for subset in itertools.combinations(range(n), r):
            ok = True
            subset_set = set(subset)
            for u, v in edges:
                if u in subset_set and v in subset_set:
                    ok = False
                    break
            if ok:
                return True
    return False


def generate_all_instances(max_n: int = 5) -> List[dict]:
    """Generate all possible graph instances up to ``max_n`` vertices.

    For each graph we iterate k in a generous range to hit edge cases.
    Invalid instances (according to the problem validators) are skipped.
    """
    instances = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        possible_edges = list(itertools.combinations(vertices, 2))
        # enumerate all subsets of possible edges
        for edge_subset in itertools.chain.from_iterable(
            itertools.combinations(possible_edges, r) for r in range(len(possible_edges) + 1)
        ):
            edges = [list(e) for e in edge_subset]
            # try a range of k values covering negatives and beyond n
            for k in range(-2, n + 3):
                instance = {"n": n, "edges": edges, "k": k}
                try:
                    problems.VertexCover.validate(instance)
                except Exception:
                    # Invalid according to the spec – skip
                    continue
                instances.append(instance)
    return instances


def main() -> None:
    source_instances = generate_all_instances()
    total = len(source_instances)
    passed = 0
    for src in source_instances:
        # compute answers for source and target
        src_ans = vertex_cover_bruteforce(src)
        tgt = reduce.reduce(src)
        # validate the reduced instance (should be a valid IndependentSet)
        try:
            problems.IndependentSet.validate(tgt)
        except Exception as e:
            print(f"Reduced instance invalid: {e}", file=sys.stderr)
            continue
        tgt_ans = independent_set_bruteforce(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", src, tgt, src_ans, tgt_ans, file=sys.stderr)
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
