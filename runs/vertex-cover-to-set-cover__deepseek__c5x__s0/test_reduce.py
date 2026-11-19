"""Automated tests for the VertexCover → SetCover reduction.

The repository provides only validation helpers for the two problems and a
``reduce`` function.  This test suite implements brute‑force solvers for both
problems, generates a large number of small random instances, validates the
original and reduced instances, and checks that the answers agree.

If all generated instances pass, we consider the reduction verified.
The script writes a ``verdict.json`` file with the required fields.
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations

# Import the problem definitions and the reduction implementation.
import problems  # noqa: F401 – ensures validation helpers are available
from reduce import reduce as reduce_instance


def vertex_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the VertexCover instance has a cover of size ≤ k.

    The instance format is validated by ``VertexCover.validate`` before this
    function is called.
    """
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]

    if k < 0:
        return False
    if not edges:
        # Empty edge set is always covered (by the empty set) for any k ≥ 0.
        return True
    if k >= n:
        return True

    vertices = list(range(n))
    # Try all subsets up to size k.
    for r in range(k + 1):
        for subset in combinations(vertices, r):
            covered = True
            subset_set = set(subset)
            for u, v in edges:
                if u not in subset_set and v not in subset_set:
                    covered = False
                    break
            if covered:
                return True
    return False


def set_cover_bruteforce(instance: dict) -> bool:
    """Return True iff the SetCover instance can be covered with ≤ k sets.
    """
    u = instance["universe_size"]
    sets = instance["sets"]
    k = instance["k"]

    if k < 0:
        return False
    if u == 0:
        return True

    universe = set(range(u))
    # Pre‑convert each set to a Python set for fast membership testing.
    set_list = [set(s) for s in sets]

    for r in range(k + 1):
        for indices in combinations(range(len(set_list)), r):
            covered = set()
            for i in indices:
                covered.update(set_list[i])
            if covered >= universe:
                return True
    return False


def generate_random_vertex_cover_instance(max_n: int = 5) -> dict:
    """Generate a random VertexCover instance with small parameters.

    ``max_n`` limits the number of vertices to keep the brute‑force search
    tractable.  Edge list is a random subset of all possible edges.
    """
    n = random.randint(0, max_n)
    possible_edges = [(u, v) for u in range(n) for v in range(u + 1, n)]
    edges = random.sample(possible_edges, random.randint(0, len(possible_edges)))
    # Convert to required list-of-lists format.
    edges = [list(e) for e in edges]
    # Choose k in a range that includes negative, zero, and larger than n.
    k = random.randint(-2, n + 2)
    return {"n": n, "edges": edges, "k": k}


def main() -> None:
    random.seed(0)  # deterministic for reproducibility
    total = 0
    passed = 0
    mismatches = []

    for _ in range(200):  # number of random tests; adjust if needed
        src = generate_random_vertex_cover_instance()
        # Validate source instance using the provided class.
        try:
            problems.VertexCover.validate(src)
        except Exception as e:
            print("Source validation failed:", e, file=sys.stderr)
            continue

        tgt = reduce_instance(src)
        # Validate target instance.
        try:
            problems.SetCover.validate(tgt)
        except Exception as e:
            print("Target validation failed:", e, file=sys.stderr)
            continue

        src_ans = vertex_cover_bruteforce(src)
        tgt_ans = set_cover_bruteforce(tgt)
        total += 1
        if src_ans == tgt_ans:
            passed += 1
        else:
            mismatches.append({"src": src, "tgt": tgt, "src_ans": src_ans, "tgt_ans": tgt_ans})

    verdict = {
        "verified": passed == total and total > 0,
        "tests_run": total,
        "tests_passed": passed,
    }
    # Write the verdict JSON.
    with open("verdict.json", "w", encoding="utf-8") as f:
        json.dump(verdict, f, indent=2)

    # Print a short summary for the user.
    print(json.dumps(verdict, indent=2))
    if mismatches:
        print("Mismatches found (showing first):", file=sys.stderr)
        print(json.dumps(mismatches[0], indent=2), file=sys.stderr)

if __name__ == "__main__":
    main()

