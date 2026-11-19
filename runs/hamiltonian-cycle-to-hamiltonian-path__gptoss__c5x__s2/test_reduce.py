"""Independent verification of reduce.py for HamiltonianCycle -> HamiltonianPath.

We implement our own brute-force solvers for both problems from the
definitions in problems.py, then compare answers on many small source
instances and their reductions.  We also check the target instance is valid
and that reduce runs in polynomial time (i.e. does not itself solve the
source by brute force).
"""

from __future__ import annotations

import itertools
import json
import time

import problems
import reduce as reduce_module
from reduce import reduce


# ----------------------------------------------------------------------
# Our own brute-force solvers (written from the problem definitions).

def _edge_set(instance):
    return {frozenset(e) for e in instance["edges"]}


def brute_hamiltonian_cycle(instance):
    """Yes iff a cycle visits every vertex exactly once and returns."""
    n = instance["n"]
    edges = _edge_set(instance)
    if n <= 2:
        return False
    for perm in itertools.permutations(range(n)):
        if all(
            frozenset((perm[i], perm[(i + 1) % n])) in edges
            for i in range(n)
        ):
            return True
    return False


def brute_hamiltonian_path(instance):
    """Yes iff a path visits every vertex exactly once (any endpoints)."""
    n = instance["n"]
    if n == 0:
        return False
    if n == 1:
        return True
    edges = _edge_set(instance)
    for perm in itertools.permutations(range(n)):
        if all(
            frozenset((perm[i], perm[i + 1])) in edges
            for i in range(n - 1)
        ):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def all_graphs(n):
    """Every simple undirected graph on vertices 0..n-1."""
    possible = [list(e) for e in itertools.combinations(range(n), 2)]
    for mask in range(1 << len(possible)):
        edges = [e for i, e in enumerate(possible) if mask & (1 << i)]
        yield {"n": n, "edges": edges}


def random_graphs(rng, n, count):
    possible = [list(e) for e in itertools.combinations(range(n), 2)]
    for _ in range(count):
        edges = [e for e in possible if rng.random() < 0.5]
        yield {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Tests.  Each returns (name, passed, detail).

def test_solvers_sanity():
    """Sanity-check our solvers against the documented edge cases."""
    checks = [
        (brute_hamiltonian_cycle, {"n": 0, "edges": []}, False),
        (brute_hamiltonian_cycle, {"n": 1, "edges": []}, False),
        (brute_hamiltonian_cycle, {"n": 2, "edges": [[0, 1]]}, False),
        (brute_hamiltonian_cycle, {"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]}, True),
        (brute_hamiltonian_cycle, {"n": 3, "edges": [[0, 1], [1, 2]]}, False),
        (brute_hamiltonian_path, {"n": 0, "edges": []}, False),
        (brute_hamiltonian_path, {"n": 1, "edges": []}, True),
        (brute_hamiltonian_path, {"n": 2, "edges": [[0, 1]]}, True),
        (brute_hamiltonian_path, {"n": 2, "edges": []}, False),
        (brute_hamiltonian_path, {"n": 3, "edges": [[0, 1], [1, 2]]}, True),
        (brute_hamiltonian_path, {"n": 3, "edges": [[0, 1]]}, False),
    ]
    for solver, inst, expected in checks:
        if solver(inst) != expected:
            return ("solvers_sanity", False,
                    f"{solver.__name__}({inst}) != {expected}")
    return ("solvers_sanity", True, f"{len(checks)} edge cases")


def test_functional_exhaustive():
    """Exhaustive: answers agree for all graphs with n = 0..5."""
    count = 0
    for n in range(0, 6):
        for inst in all_graphs(n):
            problems.HamiltonianCycle.validate(inst)
            src = brute_hamiltonian_cycle(inst)
            out = reduce(inst)
            problems.HamiltonianPath.validate(out)
            tgt = brute_hamiltonian_path(out)
            if src != tgt:
                return ("functional_exhaustive", False,
                        f"mismatch on {inst}: cycle={src}, reduced={out} path={tgt}")
            count += 1
    return ("functional_exhaustive", True, f"{count} graphs (n=0..5)")


def test_functional_random():
    """Random graphs with n = 6..8."""
    import random
    rng = random.Random(12345)
    count = 0
    for n in range(6, 9):
        for inst in random_graphs(rng, n, 60):
            src = brute_hamiltonian_cycle(inst)
            out = reduce(inst)
            problems.HamiltonianPath.validate(out)
            tgt = brute_hamiltonian_path(out)
            if src != tgt:
                return ("functional_random", False,
                        f"mismatch on {inst}: cycle={src}, reduced={out} path={tgt}")
            count += 1
    return ("functional_random", True, f"{count} random graphs (n=6..8)")


def test_output_is_valid_target():
    """reduce always returns a valid HamiltonianPath instance."""
    import random
    rng = random.Random(7)
    count = 0
    for n in range(0, 7):
        for inst in all_graphs(n):
            out = reduce(inst)
            try:
                problems.HamiltonianPath.validate(out)
            except Exception as exc:  # noqa: BLE001
                return ("output_is_valid_target", False, f"{inst} -> {out}: {exc}")
            count += 1
    return ("output_is_valid_target", True, f"{count} outputs validated")


def test_no_bruteforce_solver_call():
    """reduce must not call a brute-force solver (e.g. itertools.permutations).

    We monkeypatch itertools.permutations to raise; a genuine polynomial
    reduction never enumerates vertex permutations.
    """
    original = itertools.permutations

    def forbidden(*args, **kwargs):
        raise AssertionError("reduce called itertools.permutations (brute force)")

    itertools.permutations = forbidden
    try:
        for inst in [{"n": 5, "edges": []},
                     {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]}]:
            reduce(inst)
    except AssertionError as exc:
        return ("no_bruteforce_solver_call", False, str(exc))
    finally:
        itertools.permutations = original
    return ("no_bruteforce_solver_call", True, "no permutation enumeration observed")


def test_polynomial_time():
    """reduce must run in polynomial time; measure scaling on empty graphs.

    A polynomial-time reduction handles n = 10 instantly.  Brute force over
    permutations needs ~10! steps and takes about a second, growing ~10x per
    added vertex.
    """
    times = {}
    for n in (8, 9, 10):
        inst = {"n": n, "edges": []}
        t0 = time.perf_counter()
        reduce(inst)
        times[n] = time.perf_counter() - t0
    # Absolute budget: any polynomial reduction is far below this at n=10.
    if times[10] > 0.5:
        return ("polynomial_time", False,
                f"reduce too slow: n=10 took {times[10]:.3f}s "
                f"(times={ {k: round(v,4) for k,v in times.items()} })")
    # Growth ratio between consecutive n should not be factorial (~10x).
    ratio = times[10] / max(times[9], 1e-9)
    if ratio > 5.0:
        return ("polynomial_time", False,
                f"super-polynomial growth ratio {ratio:.1f} "
                f"(times={ {k: round(v,4) for k,v in times.items()} })")
    return ("polynomial_time", True,
            f"times={ {k: round(v,4) for k,v in times.items()} }, ratio={ratio:.2f}")


TESTS = [
    test_solvers_sanity,
    test_functional_exhaustive,
    test_functional_random,
    test_output_is_valid_target,
    test_no_bruteforce_solver_call,
    test_polynomial_time,
]


def main():
    tests_run = 0
    tests_passed = 0
    for test in TESTS:
        tests_run += 1
        name, passed, detail = test()
        status = "PASS" if passed else "FAIL"
        if passed:
            tests_passed += 1
        print(f"[{status}] {name}: {detail}")

    verified = tests_passed == tests_run
    verdict = {
        "verified": verified,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)
    return 0 if verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
