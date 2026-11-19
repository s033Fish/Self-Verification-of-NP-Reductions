"""Independent verification of reduce.py (Hamiltonian Cycle -> Hamiltonian Path).

Uses brute-force solvers written directly from the problem definitions.
Checks:
  * the reduced instance is valid for the target problem,
  * source answer == target answer on the reduced instance,
  * reduction runs in polynomial time (timed on larger instances).
"""
from __future__ import annotations

import random
import time

from problems import HamiltonianCycle, HamiltonianPath
import reduce as reduce_mod
from solvers import ham_cycle, ham_path, all_graphs

reduce = reduce_mod.reduce


def answer_source(inst):
    return ham_cycle(inst["n"], inst["edges"])


def answer_target(inst):
    return ham_path(inst["n"], inst["edges"])


def check(inst, counters):
    """Return None if correct, else an error string."""
    counters["run"] += 1
    src = answer_source(inst)
    out = reduce(inst)
    # reduced instance must be a valid target instance
    try:
        HamiltonianPath.validate(out)
    except Exception as exc:  # noqa: BLE001
        return f"invalid target instance for {inst}: {exc}"
    tgt = answer_target(out)
    if src != tgt:
        return f"MISMATCH source={inst} src_ans={src} reduced={out} tgt_ans={tgt}"
    counters["pass"] += 1
    return None


def main():
    counters = {"run": 0, "pass": 0}
    errors = []

    # Exhaustive over all labelled simple graphs for n = 0..5.
    for n in range(0, 6):
        cnt = 0
        for inst in all_graphs(n):
            cnt += 1
            err = check(inst, counters)
            if err:
                errors.append(err)
        print(f"exhaustive n={n}: {cnt} graphs checked")

    # Exhaustive random sample for n = 6 (all 2^15 = 32768 graphs).
    n = 6
    cnt = 0
    for inst in all_graphs(n):
        cnt += 1
        err = check(inst, counters)
        if err:
            errors.append(err)
    print(f"exhaustive n={n}: {cnt} graphs checked")

    # Random sparse/dense instances for n = 7..10.
    rng = random.Random(12345)
    for n in range(7, 11):
        poss = [(u, v) for u in range(n) for v in range(u + 1, n)]
        for _ in range(400):
            p = rng.random()
            edges = [list(e) for e in poss if rng.random() < p]
            inst = {"n": n, "edges": edges}
            err = check(inst, counters)
            if err:
                errors.append(err)
        # also a few structured ones: cycles and paths
        cyc = [[i, (i + 1) % n] for i in range(n)]
        path = [[i, i + 1] for i in range(n - 1)]
        for inst in ({"n": n, "edges": cyc}, {"n": n, "edges": path}):
            err = check(inst, counters)
            if err:
                errors.append(err)
        print(f"random n={n}: done")

    # Timing / polynomial check on larger instances.
    for n in (50, 200, 1000):
        poss = [(u, v) for u in range(n) for v in range(u + 1, n)]
        edges = [list(e) for e in rng.sample(poss, min(len(poss), 3 * n))]
        inst = {"n": n, "edges": edges}
        t0 = time.time()
        out = reduce(inst)
        dt = time.time() - t0
        HamiltonianPath.validate(out)
        print(f"timing n={n}: reduce took {dt:.4f}s, output n={out['n']}")
        if dt > 5.0:
            errors.append(f"reduce too slow on n={n}: {dt}s")

    print(f"\ntests_run={counters['run']} tests_passed={counters['pass']}")
    if errors:
        print("FAILURES:")
        for e in errors[:20]:
            print(" ", e)
        print(f"total failures: {len(errors)}")
    else:
        print("ALL CHECKS PASSED")

    # Write verdict.json
    import json
    verdict = {
        "verified": len(errors) == 0,
        "tests_run": counters["run"],
        "tests_passed": counters["pass"],
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
