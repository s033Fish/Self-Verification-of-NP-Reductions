"""Independent tests for reduce.py (VertexCover -> Clique).

We implement brute-force solvers for both problems directly from the
definitions in problems.py, then compare the source answer with the answer to
its reduction, over many small instances. We also check that the reduction
output is a valid target instance and that reduce runs in polynomial time
(no brute force) by inspection / scale test.
"""

from __future__ import annotations

import itertools
import json
import sys
import time

from problems import VertexCover, Clique, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force solvers, written from the definitions.

def vertex_cover_yes(instance) -> bool:
    """True iff graph has a vertex cover of AT MOST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    verts = list(range(n))
    # Try all subsets of size <= k.
    for size in range(0, k + 1):
        for subset in itertools.combinations(verts, size):
            s = set(subset)
            if all(u in s or v in s for u, v in edges):
                return True
    return False


def clique_yes(instance) -> bool:
    """True iff graph has a clique of AT LEAST k vertices."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k <= 0:
        return True
    if k > n:
        return False
    adj = [[False] * n for _ in range(n)]
    for u, v in edges:
        adj[u][v] = True
        adj[v][u] = True
    verts = list(range(n))
    # A clique of size >= k exists iff one of size exactly k exists.
    for subset in itertools.combinations(verts, k):
        ok = True
        for a, b in itertools.combinations(subset, 2):
            if not adj[a][b]:
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation

def all_graphs(n):
    """All simple undirected graphs on n labelled vertices."""
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def main() -> int:
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(cond, msg):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if cond:
            tests_passed += 1
        else:
            failures.append(msg)

    # 1) Cross-check the two solvers on the identity-ish overlap: a graph with
    #    no edges. Vertex cover yes iff k>=0; clique yes iff k<=1 (n>=1).
    #    (Sanity checks of the solvers themselves.)
    for n in range(0, 6):
        g = {"n": n, "edges": []}
        for k in range(-2, n + 3):
            check(vertex_cover_yes({"n": n, "edges": [], "k": k}) == (k >= 0),
                  f"empty graph n={n} k={k} vertex cover")
            expected_clique = (k <= 0) or (k == 1 and n >= 1)
            check(clique_yes({"n": n, "edges": [], "k": k}) == expected_clique,
                  f"empty graph n={n} k={k} clique")

    # 2) Main equivalence test over all small graphs and a range of k.
    for n in range(0, 6):
        for g in all_graphs(n):
            for k in range(-2, n + 3):
                src = {"n": n, "edges": [list(e) for e in g["edges"]], "k": k}
                VertexCover.validate(src)  # source must be valid
                try:
                    tgt = reduce(src)
                except Exception as exc:  # noqa: BLE001
                    check(False, f"reduce raised {exc!r} on {src}")
                    continue
                # target must be a valid Clique instance
                try:
                    Clique.validate(tgt)
                    valid_target = True
                except InvalidInstance as exc:
                    valid_target = False
                    check(False, f"invalid target {tgt!r} from {src}: {exc}")
                if not valid_target:
                    continue
                expected = vertex_cover_yes(src)
                got = clique_yes(tgt)
                check(got == expected,
                      f"MISMATCH src={src} -> tgt={tgt}: "
                      f"vc={expected} clique={got}")
                # Also directly compare solver-vs-solver on the source.
                check(vertex_cover_yes(src) == expected,
                      f"source solver unstable {src}")

    # 3) Polynomial-time / no-brute-force check: run on a moderately large
    #    instance and ensure it finishes quickly.
    n_big = 60
    edges_big = [[i, (i + 1) % n_big] for i in range(n_big)]
    big = {"n": n_big, "edges": edges_big, "k": n_big // 2}
    t0 = time.time()
    out_big = reduce(big)
    dt = time.time() - t0
    check(dt < 5.0, f"reduce too slow on n={n_big}: {dt:.3f}s")
    check(out_big["n"] == n_big, "big reduction n wrong")
    check(out_big["k"] == n_big - n_big // 2, "big reduction k wrong")
    # complement of a cycle C_60: each vertex adjacent to all but 2 others.
    # Just verify target validity.
    try:
        Clique.validate(out_big)
        check(True, "big target valid")
    except InvalidInstance as exc:
        check(False, f"big target invalid: {exc}")

    # 4) Malformed input should raise (contract).
    for bad in [
        {"n": -1, "edges": [], "k": 0},
        {"n": 3, "edges": [[0, 0]], "k": 1},
        {"n": 3, "edges": [[0, 1], [1, 0]], "k": 1},
        {"n": 3, "edges": [[0, 3]], "k": 1},
        {"n": 3, "edges": [], "k": 1.5},
        {"n": 3, "edges": [], "k": True},
        {"n": 3, "edges": [], "k": 1, "extra": 2},
    ]:
        raised = False
        try:
            reduce(bad)
        except InvalidInstance:
            raised = True
        except Exception:
            raised = False
        check(raised, f"reduce did not raise InvalidInstance on {bad!r}")

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print("  ", f)

    verified = (tests_run == tests_passed) and tests_run > 0
    with open("verdict.json", "w") as fh:
        json.dump({"verified": verified, "tests_run": tests_run,
                   "tests_passed": tests_passed}, fh)
    return 0 if verified else 1


if __name__ == "__main__":
    sys.exit(main())
