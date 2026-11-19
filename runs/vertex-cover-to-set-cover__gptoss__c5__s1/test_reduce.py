"""Automated tests for the VertexCover → SetCover reduction.

The script implements brute‑force solvers for both problems and checks that
the answer of the reduced SetCover instance matches the answer of the original
VertexCover instance on a comprehensive collection of small instances.

If all checks succeed we write ``verdict.json`` with ``verified: true`` and the
number of tests run/passed.  Otherwise ``verified`` is false and the counters
reflect how many tests were executed before the first failure.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import List, Dict, Tuple

from problems import VertexCover, SetCover
from reduce import reduce as reduce_instance


def vertex_cover_bruteforce(instance: Dict) -> bool:
    """Return True iff the VertexCover instance is a YES instance.

    The implementation enumerates all subsets of vertices and checks whether
    any subset of size at most ``k`` covers every edge.
    """
    n = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if not edges:
        return True
    if k >= n:
        return True

    vertices = list(range(n))
    for r in range(k + 1):
        for subset in itertools.combinations(vertices, r):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def set_cover_bruteforce(instance: Dict) -> bool:
    """Return True iff the SetCover instance is a YES instance.

    Enumerates subsets of the given sets and checks whether any collection of
    at most ``k`` sets covers the entire universe ``0..u-1``.
    """
    u = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    k = instance["k"]
    if k < 0:
        return False
    if u == 0:
        return True
    # If some element is not present in any set, answer is always no.
    all_elements = set()
    for s in sets:
        all_elements.update(s)
    if any(elem not in all_elements for elem in range(u)):
        return False
    if k >= len(sets):
        return True

    indices = list(range(len(sets)))
    for r in range(k + 1):
        for combo in itertools.combinations(indices, r):
            covered = set()
            for idx in combo:
                covered.update(sets[idx])
            if len(covered) == u:
                return True
    return False


def generate_all_graphs(max_n: int) -> List[Dict]:
    """Generate every simple undirected graph with up to ``max_n`` vertices.

    Each graph is represented as a dict matching the VertexCover instance
    format (without the ``k`` field – that will be added later).
    """
    instances: List[Dict] = []
    for n in range(max_n + 1):
        possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for r in range(len(possible_edges) + 1):
            for edges in itertools.combinations(possible_edges, r):
                instances.append({"n": n, "edges": [list(e) for e in edges]})
    return instances


def main() -> None:
    total_tests = 0
    passed_tests = 0
    base_instances = generate_all_graphs(4)
    for base in base_instances:
        n = base["n"]
        for k in range(-1, n + 2):
            total_tests += 1
            vc_instance = {"n": n, "edges": base["edges"], "k": k}
            try:
                VertexCover.validate(vc_instance)
            except Exception as exc:
                print("Validation error on source instance:", vc_instance, file=sys.stderr)
                raise
            ans_vc = vertex_cover_bruteforce(vc_instance)
            target = reduce_instance(vc_instance)
            SetCover.validate(target)
            ans_sc = set_cover_bruteforce(target)
            if ans_vc == ans_sc:
                passed_tests += 1
            else:
                print("Mismatch detected!", file=sys.stderr)
                print("Source instance:", vc_instance, file=sys.stderr)
                print("Reduced target:", target, file=sys.stderr)
                print("VertexCover answer:", ans_vc, "SetCover answer:", ans_sc, file=sys.stderr)
                verdict = {"verified": False, "tests_run": total_tests, "tests_passed": passed_tests}
                with open("verdict.json", "w") as f:
                    json.dump(verdict, f)
                sys.exit(1)
    verdict = {"verified": True, "tests_run": total_tests, "tests_passed": passed_tests}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
