"""Independent checks of reduce.py for the 3-SAT -> 1-in-3-SAT task.

Contains:
  * brute-force solvers for both problems, written from the docstrings;
  * correctness tests comparing solver answers on many small source
    instances with the answers of their reductions;
  * requirement tests, in particular that reduce() runs in polynomial
    time and does NOT call a brute-force solver.
"""

from __future__ import annotations

import itertools
import random
import subprocess
import sys
import time

import problems
import reduce as red
from problems import ThreeSat, OneInThreeSat


# ----------------------------------------------------------------------
# Brute-force solvers (independent of reduce.py)

def solve_three_sat(instance):
    """3-SAT: yes iff some assignment satisfies every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(
            any((lit > 0 and bits[abs(lit) - 1]) or (lit < 0 and not bits[abs(lit) - 1])
                for lit in clause)
            for clause in clauses
        ):
            return True
    return False


def solve_one_in_three_sat(instance):
    """Positive 1-in-3-SAT: yes iff exactly one var per clause is true."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        if all(sum(bits[v - 1] for v in clause) == 1 for clause in clauses):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generators (small, valid source instances)

def random_source_instance(rng):
    m = rng.randint(0, 5)
    clauses = []
    if m >= 3:
        n_clauses = rng.randint(0, 6)
        for _ in range(n_clauses):
            vs = rng.sample(range(1, m + 1), 3)
            clause = [v if rng.random() < 0.5 else -v for v in vs]
            clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def exhaustive_small_instances():
    """All 3-SAT instances over <= 3 variables with up to 3 clauses."""
    out = []
    for m in range(0, 4):
        if m < 3:
            out.append({"num_vars": m, "clauses": []})
            continue
        # all possible clauses over vars 1..m (3 distinct vars, any signs)
        all_clauses = []
        for vs in itertools.combinations(range(1, m + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                all_clauses.append([s * v for s, v in zip(signs, vs)])
        for k in range(0, 4):
            for combo in itertools.combinations(all_clauses, k):
                out.append({"num_vars": m, "clauses": [list(c) for c in combo]})
    return out


# ----------------------------------------------------------------------
# Test harness

RESULTS = []


def check(name, fn):
    try:
        fn()
    except Exception as exc:  # noqa: BLE001
        RESULTS.append((name, False, f"{type(exc).__name__}: {exc}"))
    else:
        RESULTS.append((name, True, ""))


# --- correctness ------------------------------------------------------

def test_random_correctness():
    rng = random.Random(12345)
    for i in range(400):
        inst = random_source_instance(rng)
        ThreeSat.validate(inst)
        out = red.reduce(inst)
        OneInThreeSat.validate(out)
        want = solve_three_sat(inst)
        got = solve_one_in_three_sat(out)
        assert want == got, f"instance #{i} {inst}: source={want} reduced={got} out={out}"


def test_exhaustive_correctness():
    for inst in exhaustive_small_instances():
        ThreeSat.validate(inst)
        out = red.reduce(inst)
        OneInThreeSat.validate(out)
        want = solve_three_sat(inst)
        got = solve_one_in_three_sat(out)
        assert want == got, f"{inst}: source={want} reduced={got} out={out}"


def test_edge_cases():
    cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 2, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, -3], [1, -2, 3],
                                    [1, -2, -3], [-1, 2, 3], [-1, 2, -3],
                                    [-1, -2, 3], [-1, -2, -3]]},
    ]
    for inst in cases:
        ThreeSat.validate(inst)
        out = red.reduce(inst)
        OneInThreeSat.validate(out)
        assert solve_three_sat(inst) == solve_one_in_three_sat(out), inst


def test_output_is_valid_target():
    rng = random.Random(999)
    for _ in range(200):
        inst = random_source_instance(rng)
        out = red.reduce(inst)
        OneInThreeSat.validate(out)  # raises InvalidInstance if malformed


# --- requirement tests ------------------------------------------------

def test_reduce_does_not_call_brute_force_solver():
    """reduce() must not call a brute-force solver (explicit requirement)."""
    calls = []
    original = red.solve_three_sat

    def spy(instance):
        calls.append(instance)
        return original(instance)

    red.solve_three_sat = spy
    try:
        red.reduce({"num_vars": 3, "clauses": [[1, 2, 3]]})
    finally:
        red.solve_three_sat = original
    assert not calls, f"reduce() called brute-force solve_three_sat {len(calls)} time(s)"


def test_reduce_polynomial_time():
    """reduce() must run in polynomial time.

    We build an unsatisfiable 3-SAT instance whose clauses only mention
    variables 1..3 but which declares num_vars = 26.  A polynomial-time
    reduction would be fast; a brute-force one must enumerate 2**26
    assignments and will not finish quickly.
    """
    clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        clauses.append([s * v for s, v in zip(signs, (1, 2, 3))])
    inst = {"num_vars": 26, "clauses": clauses}
    ThreeSat.validate(inst)
    code = (
        "import sys, time; sys.path.insert(0, '.');"
        "import reduce;"
        "t=time.time();"
        "reduce.reduce({'num_vars':26,'clauses':%r});"
        "print(time.time()-t)" % (clauses,)
    )
    try:
        proc = subprocess.run([sys.executable, "-c", code],
                              capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        raise AssertionError("reduce() did not finish within 5s on a 26-variable "
                             "unsat instance: not polynomial time")
    assert proc.returncode == 0, proc.stderr


def test_reduce_scaling():
    """Runtime growth across sizes should be polynomial, not exponential."""
    clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        clauses.append([s * v for s, v in zip(signs, (1, 2, 3))])
    times = []
    for m in (14, 16, 18):
        inst = {"num_vars": m, "clauses": clauses}
        t0 = time.time()
        red.reduce(inst)
        times.append(time.time() - t0)
    # exponential doubling per +2 vars -> ratio ~4; polynomial would be ~1.
    ratio = times[-1] / max(times[0], 1e-6)
    assert ratio < 2.5, f"runtime scaling looks exponential: times={times}"


# ----------------------------------------------------------------------

def main():
    check("random correctness (400 instances)", test_random_correctness)
    check("exhaustive correctness (small instances)", test_exhaustive_correctness)
    check("edge cases", test_edge_cases)
    check("output is valid target instance (200 instances)", test_output_is_valid_target)
    check("reduce does not call brute-force solver", test_reduce_does_not_call_brute_force_solver)
    check("reduce runs in polynomial time (26 vars, 5s timeout)", test_reduce_polynomial_time)
    check("reduce runtime scaling is polynomial", test_reduce_scaling)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    for name, ok, msg in RESULTS:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  -- {msg}" if msg else ""))
    print(f"\n{passed}/{total} checks passed")
    return passed, total


if __name__ == "__main__":
    p, t = main()
    sys.exit(0 if p == t else 1)
