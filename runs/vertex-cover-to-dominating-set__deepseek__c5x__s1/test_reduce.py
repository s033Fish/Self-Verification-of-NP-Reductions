"""Tests for the reduction from VertexCover to DominatingSet.

The repository provides only validation logic for the two problems.  To
verify the reduction we implement exhaustive (brute‑force) solvers for both
problems that are correct for the tiny instances we generate.  For each random
instance we compare the answer of the source problem with the answer of the
target problem after applying ``reduce``.

If all generated instances agree, the reduction is considered verified.
The script prints a JSON object required by the task description.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations
from typing import Dict, List, Tuple

import problems  # provides validation classes
from reduce import reduce as reduce_instance


def vertex_cover_bruteforce(instance: Dict) -> bool:
    """Return True iff the VertexCover instance has a cover of size <= k.

    The instance is assumed to be validated already.
    """
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]

    if k < 0:
        return False
    if not edges:
        return True  # empty edge set is always covered
    if k >= n:
        return True

    vertices = list(range(n))
    # try all subsets up to size k
    for size in range(k + 1):
        for subset in combinations(vertices, size):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def dominating_set_bruteforce(instance: Dict) -> bool:
    """Return True iff the DominatingSet instance has a dominating set of size <= k.
    """
    n: int = instance["n"]
    edges: List[Tuple[int, int]] = [tuple(e) for e in instance["edges"]]
    k: int = instance["k"]

    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True

    # build adjacency list including self (domination by being in the set)
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # each vertex dominates itself as well
    for i in range(n):
        adj[i].add(i)

    vertices = list(range(n))
    for size in range(k + 1):
        for subset in combinations(vertices, size):
            dominated = set()
            for v in subset:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def random_instance(max_n: int = 6, edge_prob: float = 0.4) -> Dict:
    """Generate a random VertexCover instance with n up to ``max_n``.

    The function also chooses a random integer k in a reasonable range.
    """
    n = random.randint(0, max_n)
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < edge_prob:
                edges.append([u, v])
    # pick k between -1 and n+1 to hit edge cases
    k = random.randint(-1, n + 1)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):  # number of random tests
        src = random_instance()
        # validate source instance
        problems.VertexCover.validate(src)
        src_ans = vertex_cover_bruteforce(src)
        tgt = reduce_instance(src)
        # validate target instance
        problems.DominatingSet.validate(tgt)
        tgt_ans = dominating_set_bruteforce(tgt)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            # print a diagnostic and break
            print("Mismatch!", file=sys.stderr)
            print("Source:", src, file=sys.stderr)
            print("Source answer:", src_ans, file=sys.stderr)
            print("Reduced:", tgt, file=sys.stderr)
            print("Target answer:", tgt_ans, file=sys.stderr)
            break

    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
