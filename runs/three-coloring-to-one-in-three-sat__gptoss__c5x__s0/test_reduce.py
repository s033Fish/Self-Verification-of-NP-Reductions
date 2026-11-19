"""Independent verification tests for reduce.py (3-Coloring -> 1-in-3-SAT).

We implement our own brute-force solvers for both problems directly from the
definitions in problems.py, then compare answers on many small source
instances and their reductions.  We also test the structural requirements:
the reduction output must be a valid target instance, and the reduction must
run in polynomial time without calling a brute-force solver.
"""

from __future__ import annotations

import itertools
import json
import random
import subprocess
import sys

from problems import ThreeColoring, OneInThreeSat
import reduce as reduce_module


# ----------------------------------------------------------------------
# Our own brute-force solvers (written from the problem definitions).

def solve_three_coloring(instance) -> bool:
    """True iff the graph admits a proper 3-colouring."""
    n = instance["n"]
    edges = instance["edges"]
    for assignment in itertools.product(range(3), repeat=n):
        if all(assignment[u] != assignment[v] for u, v in edges):
            return True
    return False


def solve_one_in_three_sat(instance) -> bool:
    """True iff some assignment makes exactly one var true per clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for assignment in itertools.product((False, True), repeat=m):
        if all(sum(1 for a in clause if assignment[a - 1]) == 1 for clause in clauses):
            return True
    return False


# ----------------------------------------------------------------------
# Instance generation.

def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def generate_instances():
    instances = []
    # Exhaustive over all graphs with 0..4 vertices.
    for n in range(0, 5):
        instances.extend(all_graphs(n))
    # Random larger graphs (still small enough for our brute force).
    rng = random.Random(20240517)
    for n in range(5, 8):
        pairs = list(itertools.combinations(range(n), 2))
        for _ in range(60):
            edges = [list(p) for p in pairs if rng.random() < 0.45]
            instances.append({"n": n, "edges": edges})
    # Hand-picked edge cases.
    instances.append({"n": 0, "edges": []})
    instances.append({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]]})          # K3: yes
    instances.append({"n": 4, "edges": [[0, 1], [0, 2], [0, 3],
                                        [1, 2], [1, 3], [2, 3]]})          # K4: no
    instances.append({"n": 5, "edges": [[0, 1], [0, 2], [0, 3],
                                        [1, 2], [1, 3], [2, 3]]})          # K4 + isolated: no
    instances.append({"n": 6, "edges": [[0, 1], [1, 2], [2, 0],
                                        [3, 4], [4, 5], [5, 3]]})          # two triangles: yes
    instances.append({"n": 7, "edges": [[0, 1], [1, 2], [2, 3], [3, 0],
                                        [0, 2], [1, 3]]})                  # K4-ish: no
    return instances


# ----------------------------------------------------------------------
# Individual requirement checks.

def check_reduction_matches(instances):
    """Return (run, passed, failures) for functional correctness."""
    run = passed = 0
    failures = []
    for idx, inst in enumerate(instances):
        ThreeColoring.validate(inst)
        src = solve_three_coloring(inst)
        reduced = reduce_module.reduce(inst)
        OneInThreeSat.validate(reduced)          # output must be valid target
        tgt = solve_one_in_three_sat(reduced)
        run += 1
        if src == tgt:
            passed += 1
        else:
            failures.append(
                f"instance #{idx} {inst}: source={src} target={tgt} reduced={reduced}"
            )
    return run, passed, failures


def check_polynomial_no_bruteforce(timeout=6.0):
    """Run reduce on a large NO instance; a polynomial reduction finishes fast.

    The instance is K4 on vertices 0..3 plus many isolated vertices (n=40),
    which is unsatisfiable.  A brute-force 3**40 search will not terminate.
    """
    code = (
        "import sys; sys.path.insert(0, '.');"
        "from reduce import reduce;"
        "inst = {'n': 40, 'edges': [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]};"
        "print(reduce(inst))"
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            timeout=timeout,
        )
        return proc.returncode == 0, proc.stdout.decode().strip() or proc.stderr.decode().strip()
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s (exponential/brute-force behaviour)"


def check_source_has_no_bruteforce():
    """Static check: the reduction must not contain a brute-force solver."""
    with open("reduce.py", "r") as fh:
        source = fh.read()
    suspicious = [
        "bruteforce",
        "product(range(3)",
        "3**n",
        "3 ** n",
    ]
    found = [token for token in suspicious if token in source]
    return not found, found


# ----------------------------------------------------------------------
# Main driver.

def main():
    tests_run = 0
    tests_passed = 0
    failures = []

    def record(name, ok, detail=""):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if ok:
            tests_passed += 1
        else:
            failures.append(f"{name}: {detail}")

    instances = generate_instances()
    run, passed, fails = check_reduction_matches(instances)
    tests_run += run
    tests_passed += passed
    failures.extend(fails)

    ok, detail = check_polynomial_no_bruteforce()
    record("polynomial_time_no_bruteforce", ok, detail)

    ok, found = check_source_has_no_bruteforce()
    record("source_has_no_bruteforce", ok, f"found tokens {found}")

    print(f"functional comparisons: {passed}/{run} passed")
    print(f"TOTAL TESTS_RUN={tests_run} TESTS_PASSED={tests_passed}")
    if failures:
        print("FAILURES:")
        for f in failures[:20]:
            print("  -", f)
        if len(failures) > 20:
            print(f"  ... and {len(failures) - 20} more")

    verified = (tests_passed == tests_run)
    with open("verdict.json", "w") as fh:
        json.dump(
            {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed},
            fh,
            indent=2,
        )
        fh.write("\n")
    print("wrote verdict.json:", {"verified": verified,
                                  "tests_run": tests_run,
                                  "tests_passed": tests_passed})


if __name__ == "__main__":
    main()
