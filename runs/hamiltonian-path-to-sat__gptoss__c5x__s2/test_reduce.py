"""Independent tests for reduce.py (Hamiltonian Path -> SAT).

We implement our own solvers from the definitions in problems.py:

  * solve_hp_bruteforce  -- try every permutation of the vertices.
  * solve_sat_bruteforce -- try every truth assignment (small formulas).
  * solve_sat_dpll       -- a complete DPLL solver, used only for the
                            larger reduced formulas where 2^m is too big.

The tests compare the SOURCE answer with the TARGET answer of the
reduction on many small instances (exhaustive for n <= 4, random for
larger n), validate the shape of the produced SAT instances, check the
documented edge cases, and sanity-check that reduce runs in polynomial
time (no brute force).
"""

import itertools
import json
import random
import time

from problems import HamiltonianPath, Sat, InvalidInstance
from reduce import reduce


# ----------------------------------------------------------------------
# Brute-force / complete solvers written from the definitions
# ----------------------------------------------------------------------

def solve_hp_bruteforce(instance):
    """True iff the undirected graph has a Hamiltonian path (any endpoints)."""
    n = instance["n"]
    if n == 0:
        return False
    if n == 1:
        return True
    edges = {frozenset(e) for e in instance["edges"]}
    for perm in itertools.permutations(range(n)):
        if all(frozenset((perm[i], perm[i + 1])) in edges
               for i in range(n - 1)):
            return True
    return False


def solve_sat_bruteforce(instance):
    """True iff some assignment satisfies every clause (enumerate all)."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            if not any(((lit > 0) == bool((bits >> (abs(lit) - 1)) & 1))
                       for lit in clause):
                ok = False
                break
        if ok:
            return True
    return False


def solve_sat_dpll(instance):
    """Complete DPLL SAT solver (unit propagation + branching)."""
    def simplify(clauses, var, value):
        true_lit = var if value else -var
        false_lit = -var if value else var
        out = []
        for clause in clauses:
            if true_lit in clause:
                continue
            if false_lit in clause:
                out.append(tuple(l for l in clause if l != false_lit))
            else:
                out.append(clause)
        return out

    def dpll(clauses):
        while True:
            if any(len(c) == 0 for c in clauses):
                return False
            if not clauses:
                return True
            unit = next((c[0] for c in clauses if len(c) == 1), None)
            if unit is None:
                break
            clauses = simplify(clauses, abs(unit), unit > 0)
        var = abs(clauses[0][0])
        return (dpll(simplify(clauses, var, True)) or
                dpll(simplify(clauses, var, False)))

    return dpll([tuple(c) for c in instance["clauses"]])


def solve_sat(instance):
    """Use brute force when feasible, else the complete DPLL solver."""
    if instance["num_vars"] <= 20:
        return solve_sat_bruteforce(instance)
    return solve_sat_dpll(instance)


# ----------------------------------------------------------------------
# Instance generators
# ----------------------------------------------------------------------

def all_graphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        edges = [list(p) for i, p in enumerate(pairs) if (mask >> i) & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, p, rng):
    edges = [[u, v] for u, v in itertools.combinations(range(n), 2)
             if rng.random() < p]
    return {"n": n, "edges": edges}


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

RESULTS = []


def check(name, fn):
    try:
        fn()
    except Exception as exc:  # noqa: BLE001
        RESULTS.append((name, False, repr(exc)))
    else:
        RESULTS.append((name, True, ""))


def assert_reduction_matches(instance):
    """Core property: source answer == target answer of the reduction."""
    src = solve_hp_bruteforce(instance)
    out = reduce(instance)
    # The reduction must emit a well-formed SAT instance.
    Sat.validate(out)
    tgt = solve_sat(out)
    assert src == tgt, (
        f"mismatch on {instance}: hp={src}, sat={tgt}, reduction={out}"
    )


def main():
    rng = random.Random(12345)

    # --- exhaustive over all graphs for n = 0..4 -------------------------
    for n in range(0, 5):
        for idx, inst in enumerate(all_graphs(n)):
            check(f"exhaustive n={n} graph#{idx}", lambda i=inst: assert_reduction_matches(i))

    # --- random graphs, larger n ----------------------------------------
    for n in (5, 6, 7):
        for p in (0.2, 0.35, 0.5, 0.75, 1.0):
            for k in range(8):
                inst = random_graph(n, p, rng)
                check(f"random n={n} p={p} k={k}",
                      lambda i=inst: assert_reduction_matches(i))

    # --- explicit documented edge cases ---------------------------------
    def edge_n0():
        inst = {"n": 0, "edges": []}
        assert solve_hp_bruteforce(inst) is False
        out = reduce(inst)
        Sat.validate(out)
        assert solve_sat(out) is False
        assert [] in out["clauses"]

    def edge_n1():
        inst = {"n": 1, "edges": []}
        assert solve_hp_bruteforce(inst) is True
        out = reduce(inst)
        Sat.validate(out)
        assert solve_sat(out) is True

    def edge_n2_no():
        inst = {"n": 2, "edges": []}
        assert solve_hp_bruteforce(inst) is False
        assert solve_sat(reduce(inst)) is False

    def edge_n2_yes():
        inst = {"n": 2, "edges": [[0, 1]]}
        assert solve_hp_bruteforce(inst) is True
        assert solve_sat(reduce(inst)) is True

    def edge_n2_reversed():
        inst = {"n": 2, "edges": [[1, 0]]}
        assert solve_hp_bruteforce(inst) is True
        assert solve_sat(reduce(inst)) is True

    def path_graph_yes():
        inst = {"n": 5, "edges": [[0, 1], [1, 2], [2, 3], [3, 4]]}
        assert solve_hp_bruteforce(inst) is True
        assert solve_sat(reduce(inst)) is True

    def star_graph_no():
        inst = {"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]]}
        assert solve_hp_bruteforce(inst) is False
        assert solve_sat(reduce(inst)) is False

    def disconnected_no():
        inst = {"n": 4, "edges": [[0, 1], [2, 3]]}
        assert solve_hp_bruteforce(inst) is False
        assert solve_sat(reduce(inst)) is False

    for nm, fn in [("edge n=0", edge_n0), ("edge n=1", edge_n1),
                   ("edge n=2 no edge", edge_n2_no),
                   ("edge n=2 edge", edge_n2_yes),
                   ("edge n=2 reversed edge", edge_n2_reversed),
                   ("path graph n=5 yes", path_graph_yes),
                   ("star graph n=5 no", star_graph_no),
                   ("disconnected n=4 no", disconnected_no)]:
        check(nm, fn)

    # --- output shape for n >= 2 ----------------------------------------
    def shape():
        for n in (2, 3, 4, 5):
            out = reduce({"n": n, "edges": []})
            Sat.validate(out)
            assert out["num_vars"] == n * n
            assert isinstance(out["clauses"], list)

    check("output shape num_vars == n*n", shape)

    # --- malformed input is rejected ------------------------------------
    def rejects_bad():
        bad = [
            {"n": -1, "edges": []},
            {"n": 2, "edges": [[0, 0]]},
            {"n": 2, "edges": [[0, 2]]},
            {"n": 2, "edges": [[0, 1], [1, 0]]},
            {"n": 2},
        ]
        for inst in bad:
            try:
                reduce(inst)
            except InvalidInstance:
                continue
            raise AssertionError(f"reduce accepted malformed {inst}")

    check("rejects malformed instances", rejects_bad)

    # --- polynomial-time sanity check (no brute force) ------------------
    def polynomial_time():
        n = 60
        inst = {"n": n, "edges": [[i, i + 1] for i in range(n - 1)]}
        start = time.time()
        out = reduce(inst)
        elapsed = time.time() - start
        Sat.validate(out)
        assert elapsed < 15.0, f"reduce took {elapsed:.2f}s for n={n}"
        # A path graph is a yes instance; the DPLL solver should confirm.
        assert solve_sat_dpll(out) is True

    check("polynomial-time sanity n=60", polynomial_time)

    tests_run = len(RESULTS)
    tests_passed = sum(1 for _, ok, _ in RESULTS if ok)
    failures = [(nm, msg) for nm, ok, msg in RESULTS if not ok]

    for nm, ok, msg in RESULTS:
        if not ok:
            print(f"FAIL: {nm}: {msg}")
    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    print(f"failures={len(failures)}")

    verdict = {
        "verified": tests_passed == tests_run,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)


if __name__ == "__main__":
    main()
