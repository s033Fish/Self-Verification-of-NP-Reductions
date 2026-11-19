"""Tests for the 3-Coloring -> 1-in-3-SAT reduction.

Contains independent brute-force / backtracking solvers for both problems
(problems.py provides no solvers) and compares answers on many small
instances.  Writes verdict.json at the end.
"""

from __future__ import annotations

import itertools
import json
import random

from problems import SOURCE, TARGET
from reduce import reduce


# ----------------------------------------------------------------------
# Solvers written from the problem definitions.

def solve_coloring(instance: dict) -> bool:
    """Brute force 3-colourability."""
    n = instance["n"]
    edges = instance["edges"]
    for colouring in itertools.product(range(3), repeat=n):
        if all(colouring[u] != colouring[v] for u, v in edges):
            return True
    return False


def solve_one_in_three(instance: dict) -> bool:
    """Backtracking solver for positive 1-in-3-SAT with propagation."""
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]
    val: list = [None] * (m + 1)  # index 1..m

    def propagate() -> bool:
        changed = True
        while changed:
            changed = False
            for a, b, c in clauses:
                trues = 0
                unknown = []
                for x in (a, b, c):
                    if val[x] is True:
                        trues += 1
                    elif val[x] is None:
                        unknown.append(x)
                if trues > 1:
                    return False
                if trues == 1:
                    for x in unknown:
                        val[x] = False
                        changed = True
                else:
                    if not unknown:
                        return False  # all three false
                    if len(unknown) == 1:
                        val[unknown[0]] = True
                        changed = True
        return True

    def rec() -> bool:
        saved = val[:]
        if not propagate():
            val[:] = saved
            return False
        idx = None
        for i in range(1, m + 1):
            if val[i] is None:
                idx = i
                break
        if idx is None:
            return True
        for choice in (True, False):
            val[idx] = choice
            if rec():
                return True
            val[:] = saved
        val[:] = saved
        return False

    return rec()


# ----------------------------------------------------------------------
# Test harness.

TESTS_RUN = 0
TESTS_PASSED = 0
FAILURES: list[str] = []


def check(instance: dict, label: str) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    expected = solve_coloring(instance)
    reduced = reduce(instance)
    try:
        TARGET.validate(reduced)
    except Exception as exc:  # noqa: BLE001
        FAILURES.append(f"{label}: reduced instance invalid: {exc}")
        return
    got = solve_one_in_three(reduced)
    if got == expected:
        TESTS_PASSED += 1
    else:
        FAILURES.append(
            f"{label}: source={expected} target={got} instance={instance} "
            f"reduced={reduced}"
        )


def all_graphs(n: int):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def main() -> None:
    # Exhaustive over all graphs with up to 4 vertices.
    for n in range(0, 5):
        for inst in all_graphs(n):
            check(inst, f"exhaustive n={n}")

    # Explicit edge cases.
    check({"n": 0, "edges": []}, "empty graph")
    check({"n": 4, "edges": [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3]]}, "K4")
    check({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, "triangle")
    check({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]]}, "star K1,4")

    # Random graphs on 5 and 6 vertices (limited edge count so the
    # brute-force target solver stays fast).
    rng = random.Random(12345)
    for n in (5, 6):
        pairs = list(itertools.combinations(range(n), 2))
        for _ in range(150):
            k = rng.randint(0, min(len(pairs), 6))
            chosen = rng.sample(pairs, k)
            inst = {"n": n, "edges": [list(e) for e in chosen]}
            check(inst, f"random n={n}")

    verdict = {
        "verified": len(FAILURES) == 0,
        "tests_run": TESTS_RUN,
        "tests_passed": TESTS_PASSED,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print(json.dumps(verdict))
    for failure in FAILURES[:20]:
        print("FAIL:", failure)
    if FAILURES:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
