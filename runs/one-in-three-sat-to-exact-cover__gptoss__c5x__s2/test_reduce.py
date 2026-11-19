"""Independent tests for reduce.py (1-in-3-SAT -> Exact Cover).

We implement brute-force solvers for both problems from the definitions in
problems.py, then compare the source answer with the answer of the reduced
target instance on many small instances.  We also check structural
requirements: the output must be a valid ExactCover instance, and reduce must
run in polynomial time (checked with a subprocess timeout on a large,
trivially-satisfiable instance).
"""

import random
import subprocess
import sys
import time

from problems import OneInThreeSat, ExactCover
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.
# ----------------------------------------------------------------------

def solve_one_in_three_sat(instance):
    """True iff some assignment makes exactly one var true in every clause."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        ok = True
        for (a, b, c) in clauses:
            cnt = ((bits >> (a - 1)) & 1) + ((bits >> (b - 1)) & 1) + ((bits >> (c - 1)) & 1)
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance):
    """True iff some subcollection of sets is disjoint and covers 0..u-1.

    DP over the covered-element bitmask.  We deduplicate identical sets and
    only ever add a set disjoint from what is already covered, so the state
    space is 2**u regardless of how many sets the instance lists.
    """
    u = instance["universe_size"]
    target = (1 << u) - 1
    masks = set()
    for s in instance["sets"]:
        m = 0
        for e in s:
            m |= 1 << e
        masks.add(m)
    masks = list(masks)
    reachable = {0}
    frontier = [0]
    while frontier:
        cur = frontier.pop()
        if cur == target:
            return True
        for m in masks:
            if cur & m:
                continue
            nxt = cur | m
            if nxt not in reachable:
                reachable.add(nxt)
                frontier.append(nxt)
    return target in reachable


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

class Harness:
    def __init__(self):
        self.run = 0
        self.passed = 0
        self.failures = []

    def check(self, name, condition):
        self.run += 1
        if condition:
            self.passed += 1
        else:
            self.failures.append(name)


def random_instance(rng, max_vars=6, max_clauses=5):
    m = rng.randint(0, max_vars)
    clauses = []
    if m >= 3:
        for _ in range(rng.randint(0, max_clauses)):
            clauses.append(sorted(rng.sample(range(1, m + 1), 3)))
    return {"num_vars": m, "clauses": clauses}


def main():
    h = Harness()
    rng = random.Random(12345)

    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [1, 2, 4], [3, 4, 1]]},
        {"num_vars": 5, "clauses": [[1, 2, 3], [3, 4, 5], [1, 4, 5]]},
    ]

    instances = list(edge_cases)
    for _ in range(400):
        instances.append(random_instance(rng))

    for idx, inst in enumerate(instances):
        try:
            OneInThreeSat.validate(inst)
        except Exception:
            h.check(f"source-valid-{idx}", False)
            continue

        src_ans = solve_one_in_three_sat(inst)

        try:
            reduced = reduce_mod.reduce(inst)
        except Exception:
            h.check(f"reduce-runs-{idx}", False)
            continue

        try:
            ExactCover.validate(reduced)
            h.check(f"target-valid-{idx}", True)
        except Exception:
            h.check(f"target-valid-{idx}", False)
            continue

        tgt_ans = solve_exact_cover(reduced)
        h.check(f"answer-match-{idx}", src_ans == tgt_ans)

    # ---- Polynomial-time requirement ---------------------------------
    # Large but trivial instance: m variables, no clauses -> always YES.
    # A polynomial reduction must return quickly.  We run it in a subprocess
    # with a hard timeout so an exponential implementation cannot hang us.
    probe = (
        "import reduce;"
        "r = reduce.reduce({'num_vars': 32, 'clauses': []});"
        "print(len(r['sets']))"
    )
    poly_ok = True
    try:
        start = time.time()
        res = subprocess.run(
            [sys.executable, "-c", probe],
            cwd=".",
            capture_output=True,
            timeout=15,
        )
        elapsed = time.time() - start
        if res.returncode != 0:
            poly_ok = False
            print("poly probe failed:", res.stderr.decode()[:500])
        else:
            print(f"poly probe (m=32, no clauses) finished in {elapsed:.2f}s, "
                  f"num_sets={res.stdout.decode().strip()}")
    except subprocess.TimeoutExpired:
        poly_ok = False
        print("poly probe (m=32, no clauses) TIMED OUT after 15s -> exponential")
    h.check("polynomial-time", poly_ok)

    print(f"\ntests_run={h.run} tests_passed={h.passed}")
    if h.failures:
        print("FAILURES:", h.failures[:20], "..." if len(h.failures) > 20 else "")
    return h


if __name__ == "__main__":
    main()
