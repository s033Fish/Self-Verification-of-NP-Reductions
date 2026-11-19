"""Independent tests for reduce.py: 3-Coloring -> 1-in-3-SAT.

We implement our own brute-force solvers for both problems from the
definitions in problems.py, then compare answers on many small source
instances and their reductions.
"""

import itertools
import random

from problems import ThreeColoring, OneInThreeSat
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.

def solve_three_coloring(instance):
    """True iff the graph is 3-colourable (brute force over 3^n)."""
    n = instance["n"]
    edges = instance["edges"]
    for colours in itertools.product(range(3), repeat=n):
        if all(colours[u] != colours[v] for u, v in edges):
            return True
    return False


def solve_one_in_three(instance):
    """True iff the positive 1-in-3-SAT formula is satisfiable.

    Backtracking over all 2^m assignments with pruning: a clause is
    rejected as soon as it has more than one true literal, or is fully
    assigned with a count different from one.
    """
    m = instance["num_vars"]
    clauses = [tuple(c) for c in instance["clauses"]]
    assign = [None] * (m + 1)

    def consistent():
        for clause in clauses:
            true_count = 0
            unassigned = 0
            for lit in clause:
                if assign[lit] is None:
                    unassigned += 1
                elif assign[lit]:
                    true_count += 1
            if true_count > 1:
                return False
            if unassigned == 0 and true_count != 1:
                return False
        return True

    def rec(i):
        if i > m:
            return consistent()
        for val in (False, True):
            assign[i] = val
            if consistent() and rec(i + 1):
                return True
        assign[i] = None
        return False

    return rec(1)


# ----------------------------------------------------------------------
# Helpers.

def all_graphs(n):
    """Yield every simple undirected graph on n vertices."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(e) for i, e in enumerate(possible) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def check(instance, label):
        nonlocal tests_run, tests_passed
        tests_run += 1
        try:
            ThreeColoring.validate(instance)
        except Exception as exc:  # pragma: no cover
            failures.append((label, "source invalid", repr(exc)))
            return
        expected = solve_three_coloring(instance)
        try:
            target = reduce_mod.reduce(instance)
        except Exception as exc:
            failures.append((label, "reduce raised", repr(exc)))
            return
        # Target must be a valid 1-in-3-SAT instance.
        try:
            OneInThreeSat.validate(target)
        except Exception as exc:
            failures.append((label, "target invalid", repr(exc)))
            return
        got = solve_one_in_three(target)
        if got != expected:
            failures.append(
                (label, f"mismatch source={expected} target={got}", instance, target)
            )
        else:
            tests_passed += 1

    # Exhaustive over all graphs for n = 0..5.
    for n in range(0, 6):
        for g in all_graphs(n):
            check(g, f"exhaustive n={n} edges={g['edges']}")

    # Random larger graphs.
    rng = random.Random(12345)
    for n in range(6, 10):
        for _ in range(300):
            g = random_graph(n, rng.choice([0.1, 0.3, 0.5, 0.8, 1.0]), rng)
            check(g, f"random n={n} edges={g['edges']}")

    print(f"tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:20]:
        print("FAILURE:", f)
    return tests_run, tests_passed, failures



def extra_edge_case_tests():
    """Targeted structural / edge-case checks, appended to the suite."""
    import time
    results = []

    def run(instance, expected, label):
        ThreeColoring.validate(instance)
        got_src = solve_three_coloring(instance)
        target = reduce_mod.reduce(instance)
        OneInThreeSat.validate(target)
        got_tgt = solve_one_in_three(target)
        ok = (got_src == expected) and (got_tgt == expected)
        results.append((label, ok, got_src, got_tgt, target))

    # n = 0
    run({"n": 0, "edges": []}, True, "n=0")
    # triangle
    run({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, True, "K3")
    # K4 (no)
    run({"n": 4, "edges": [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]}, False, "K4")
    # K5 (no)
    run({"n": 5, "edges": [[u,v] for u in range(5) for v in range(u+1,5)]}, False, "K5")
    # K3,3 (no, chromatic number 2? no: bipartite -> 2-colorable -> yes)
    run({"n": 6, "edges": [[u, 3+v] for u in range(3) for v in range(3)]}, True, "K3,3")
    # odd cycle C5 (yes)
    run({"n": 5, "edges": [[0,1],[1,2],[2,3],[3,4],[4,0]]}, True, "C5")
    # Petersen graph (3-chromatic, yes)
    pet = [(0,1),(1,2),(2,3),(3,4),(4,0),(0,5),(1,6),(2,7),(3,8),(4,9),
           (5,7),(7,9),(9,6),(6,8),(8,5)]
    run({"n": 10, "edges": [list(e) for e in pet]}, True, "Petersen")

    # Output size must be polynomial: vars = 3n + 3|E|, clauses = n + 3|E|.
    g = {"n": 7, "edges": [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,0]]}
    t = reduce_mod.reduce(g)
    assert t["num_vars"] == 3 * 7 + 3 * 7, t["num_vars"]
    assert len(t["clauses"]) == 7 + 3 * 7, len(t["clauses"])

    # Malformed source instances must raise, not silently produce garbage.
    for bad in [{"n": -1, "edges": []},
                {"n": 2, "edges": [[0, 0]]},
                {"n": 2, "edges": [[0, 1], [1, 0]]},
                {"n": 2, "edges": [[0, 5]]},
                {"n": 2}]:
        try:
            reduce_mod.reduce(bad)
            results.append((f"malformed {bad}", False, None, None, None))
        except Exception:
            results.append((f"malformed {bad}", True, None, None, None))

    # Runtime on a moderately large graph (polynomial, no solver call).
    big = {"n": 60, "edges": [[u, v] for u in range(60) for v in range(u+1, 60) if (u+v) % 3 == 0]}
    start = time.time()
    tb = reduce_mod.reduce(big)
    elapsed = time.time() - start
    OneInThreeSat.validate(tb)
    results.append((f"big graph runtime {elapsed:.3f}s", elapsed < 5.0, None, None, None))

    for label, ok, a, b, _ in results:
        print(f"{'ok ' if ok else 'FAIL'} {label} src={a} tgt={b}")
    return results


if __name__ == "__main__":
    import json

    # Part 1: exhaustive + random comparison of solvers on source vs reduction.
    n_run, n_pass, failures = main()

    # Part 2: targeted structural / edge-case checks.
    results = extra_edge_case_tests()
    extra_run = len(results)
    extra_pass = sum(1 for r in results if r[1])
    failures = list(failures) + [r for r in results if not r[1]]

    tests_run = n_run + extra_run
    tests_passed = n_pass + extra_pass
    verified = (tests_run == tests_passed) and (n_run == n_pass)

    print(f"TOTAL tests_run={tests_run} tests_passed={tests_passed} failures={len(failures)}")
    for f in failures[:20]:
        print("FAILURE:", f)

    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": bool(verified), "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
        )
        fh.write("\n")
    print("wrote verdict.json")
    if not verified:
        raise SystemExit("TESTS FAILED")
