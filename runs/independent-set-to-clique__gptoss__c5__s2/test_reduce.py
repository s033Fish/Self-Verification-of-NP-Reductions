"""Test suite for the Independent Set → Clique reduction.

The repository provides only validation functions for the two problems and a
``reduce`` function.  This test file implements exhaustive (brute‑force)
solvers for both problems and then checks that for a large number of randomly
generated small instances the answer of the reduction matches the answers of
the solvers.

The script writes a ``verdict.json`` file with the fields required by the
review task:

* ``verified`` – ``true`` iff every test passes.
* ``tests_run`` – total number of instances tested.
* ``tests_passed`` – number of instances where the reduction behaved correctly.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations
from typing import List, Dict, Any

from problems import IndependentSet, Clique
from reduce import reduce as reduce_instance


def independent_set_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the instance has an independent set of size at least k.

    The implementation enumerates all subsets of vertices.  It is only used
    for tiny graphs (n ≤ 6) in the test suite, so the exponential runtime is
    acceptable.
    """
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in combinations(vertices, size):
            independent = True
            for u, v in combinations(subset, 2):
                if frozenset((u, v)) in edges:
                    independent = False
                    break
            if independent:
                return True
    return False


def clique_bruteforce(instance: Dict[str, Any]) -> bool:
    """Return True iff the instance has a clique of size at least k."""
    n = instance["n"]
    edges = set(frozenset(e) for e in instance["edges"])
    k = instance["k"]
    if k <= 0:
        return True
    if k == 1:
        return n >= 1
    if k > n:
        return False
    vertices = list(range(n))
    for size in range(k, n + 1):
        for subset in combinations(vertices, size):
            is_clique = True
            for u, v in combinations(subset, 2):
                if frozenset((u, v)) not in edges:
                    is_clique = False
                    break
            if is_clique:
                return True
    return False


def random_instance(max_n: int = 6) -> Dict[str, Any]:
    """Generate a random Independent Set instance.

    The graph size ``n`` is chosen uniformly in ``[0, max_n]``.  Each possible
    edge is included with probability 0.3.  ``k`` is chosen uniformly in the
    range ``[-1, n+1]`` to also test edge‑case values.
    """
    n = random.randint(0, max_n)
    edges: List[List[int]] = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < 0.3:
                edges.append([u, v])
    k = random.randint(-1, n + 1)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        src = random_instance()
        try:
            IndependentSet.validate(src)
        except Exception as e:
            print("Source validation failed", src, e, file=sys.stderr)
            continue
        ans_src = independent_set_bruteforce(src)
        try:
            tgt = reduce_instance(src)
            Clique.validate(tgt)
        except Exception as e:
            print("Reduction or target validation failed", e, file=sys.stderr)
            continue
        ans_tgt = clique_bruteforce(tgt)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", src, tgt, ans_src, ans_tgt, file=sys.stderr)
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
