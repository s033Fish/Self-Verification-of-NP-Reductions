"""Independent verification of reduce.py: Vertex Cover -> SAT.

We implement our own solvers (no solvers exist in problems.py) and compare
answers on many small source instances and their reductions.
"""

from __future__ import annotations

import itertools
import random
import sys

from problems import SOURCE, TARGET
import reduce as reduce_mod


# ----------------------------------------------------------------------
# Brute-force solvers written from the problem definitions.
# ----------------------------------------------------------------------

def brute_force_vertex_cover(instance: dict) -> bool:
    """True iff there is a vertex cover of size at most k."""
    n = instance["n"]
    edges = instance["edges"]
    k = instance["k"]
    if k < 0:
        return False
    # Try all subsets of size <= k (only feasible for small n).
    for size in range(0, min(k, n) + 1):
        for subset in itertools.combinations(range(n), size):
            chosen = set(subset)
            if all(u in chosen or v in chosen for (u, v) in edges):
                return True
    return False


def brute_force_sat(instance: dict) -> bool:
    """True iff the CNF formula is satisfiable. DPLL with unit propagation."""
    clauses = [tuple(c) for c in instance["clauses"]]

    def dpll(clauses, assignment):
        # Simplify under current assignment.
        simplified = []
        for c in clauses:
            satisfied = False
            rest = []
            for lit in c:
                var = abs(lit)
                if var in assignment:
                    if assignment[var] == (lit > 0):
                        satisfied = True
                        break
                else:
                    rest.append(lit)
            if satisfied:
                continue
            if not rest:
                return False
            simplified.append(tuple(rest))
        clauses = simplified

        # Unit propagation.
        while True:
            unit = None
            for c in clauses:
                if len(c) == 1:
                    unit = c[0]
                    break
            if unit is None:
                break
            var, val = abs(unit), unit > 0
            assignment = dict(assignment)
            assignment[var] = val
            new_clauses = []
            for c in clauses:
                satisfied = False
                rest = []
                for lit in c:
                    v = abs(lit)
                    if v in assignment:
                        if assignment[v] == (lit > 0):
                            satisfied = True
                            break
                    else:
                        rest.append(lit)
                if satisfied:
                    continue
                if not rest:
                    return False
                new_clauses.append(tuple(rest))
            clauses = new_clauses

        if not clauses:
            return True
        var = abs(clauses[0][0])
        for val in (True, False):
            a2 = dict(assignment)
            a2[var] = val
            if dpll(clauses, a2):
                return True
        return False

    return dpll(clauses, {})


def brute_force_sat_enumerate(instance: dict) -> bool:
    """Pure enumeration solver, used to cross-check the DPLL solver."""
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product((False, True), repeat=m):
        ok = True
        for c in clauses:
            if not any(bits[abs(lit) - 1] == (lit > 0) for lit in c):
                ok = False
                break
        if ok:
            return True
    return False


# ----------------------------------------------------------------------
# Test harness
# ----------------------------------------------------------------------

TESTS_RUN = 0
TESTS_PASSED = 0
FAILURES = []


def check(condition: bool, label: str) -> None:
    global TESTS_RUN, TESTS_PASSED
    TESTS_RUN += 1
    if condition:
        TESTS_PASSED += 1
    else:
        FAILURES.append(label)
        print("FAIL:", label)


def all_graphs(n: int):
    """All simple graphs on n labelled vertices (each undirected edge optional)."""
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(possible)):
        edges = [list(possible[i]) for i in range(len(possible)) if mask & (1 << i)]
        yield {"n": n, "edges": edges}


def compare_instance(inst: dict, label: str) -> None:
    expected = brute_force_vertex_cover(inst)
    try:
        red = reduce_mod.reduce(inst)
    except Exception as exc:  # noqa: BLE001
        check(False, f"{label}: reduce raised {exc!r}")
        return
    # The reduction must produce a valid target instance.
    try:
        TARGET.validate(red)
        valid = True
    except Exception:  # noqa: BLE001
        valid = False
    check(valid, f"{label}: reduced instance invalid: {red!r}")
    if not valid:
        return
    got = brute_force_sat(red)
    check(got == expected, f"{label}: expected {expected}, reduction gives {got} (inst={inst}, red={red})")


def main() -> None:
    random.seed(12345)

    # --- 0. Cross-check the two SAT solvers on tiny formulas -----------
    tiny_formulas = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 0, "clauses": [[]]},
        {"num_vars": 1, "clauses": [[1]]},
        {"num_vars": 1, "clauses": [[-1]]},
        {"num_vars": 1, "clauses": [[1], [-1]]},
        {"num_vars": 2, "clauses": [[1, 2], [-1, 2], [1, -2], [-1, -2]]},
        {"num_vars": 2, "clauses": [[1, -1]]},
        {"num_vars": 3, "clauses": [[1, 2], [-1, 3], [-2, -3]]},
    ]
    for i, f in enumerate(tiny_formulas):
        a = brute_force_sat(f)
        b = brute_force_sat_enumerate(f)
        check(a == b, f"solver cross-check {i}: dpll={a} enum={b}")

    # --- 1. Exhaustive small graphs, all relevant k --------------------
    for n in range(0, 5):
        for graph in all_graphs(n):
            for k in range(-1, n + 2):
                inst = {"n": graph["n"], "edges": graph["edges"], "k": k}
                compare_instance(inst, f"exhaustive n={n} k={k} edges={graph['edges']}")

    # --- 2. Random larger graphs (DPLL handles the aux variables) ------
    for trial in range(400):
        n = random.randint(0, 9)
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        random.shuffle(possible)
        m = random.randint(0, len(possible))
        edges = [list(e) for e in possible[:m]]
        k = random.randint(-2, n + 2)
        inst = {"n": n, "edges": edges, "k": k}
        compare_instance(inst, f"random trial={trial} n={n} k={k} m={m}")

    # --- 3. Targeted cardinality-encoding test -------------------------
    # Fix the x variables to every possible assignment and check that the
    # reduced formula is satisfiable iff at most k x's are true.
    for n in range(1, 7):
        for k in range(0, n + 1):
            # Use a graph with a single edge so edge clauses do not interfere
            # (they are satisfiable under any x with at least one endpoint set).
            inst = {"n": n, "edges": [], "k": k}
            red = reduce_mod.reduce(inst)
            for bits in itertools.product((False, True), repeat=n):
                # Build formula with x fixed.
                fixed = {"num_vars": red["num_vars"],
                         "clauses": list(red["clauses"])}
                for v in range(n):
                    fixed["clauses"].append([v + 1] if bits[v] else [-(v + 1)])
                sat = brute_force_sat(fixed)
                cover_ok = sum(bits) <= k
                # Edgeless graph: any x assignment with <= k trues is a cover.
                expected = cover_ok
                check(sat == expected,
                      f"cardinality n={n} k={k} bits={bits}: sat={sat} expected={expected}")

    # --- 4. Specific documented edge cases -----------------------------
    edge_cases = [
        ({"n": 0, "edges": [], "k": -1}, False),
        ({"n": 0, "edges": [], "k": 0}, True),
        ({"n": 0, "edges": [], "k": 5}, True),
        ({"n": 3, "edges": [], "k": 0}, True),
        ({"n": 3, "edges": [[0, 1]], "k": 0}, False),
        ({"n": 3, "edges": [[0, 1]], "k": 1}, True),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 1}, False),
        ({"n": 3, "edges": [[0, 1], [1, 2], [0, 2]], "k": 2}, True),
        ({"n": 4, "edges": [[0, 1], [2, 3]], "k": 2}, True),
        ({"n": 4, "edges": [[0, 1], [2, 3]], "k": 1}, False),
        ({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 1}, True),
        ({"n": 5, "edges": [[0, 1], [0, 2], [0, 3], [0, 4]], "k": 0}, False),
    ]
    for inst, expected in edge_cases:
        red = reduce_mod.reduce(inst)
        got = brute_force_sat(red)
        check(got == expected, f"edge case {inst}: expected {expected}, got {got}")

    # --- 5. Check reduce does not call a solver / is polynomial ---------
    # Inspect the AST (not prose) for imports and calls to solver-like names.
    import ast as _ast
    tree = _ast.parse(open("reduce.py").read())
    imported = set()
    called = set()
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, _ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[0])
        elif isinstance(node, _ast.Call):
            fn = node.func
            if isinstance(fn, _ast.Name):
                called.add(fn.id)
            elif isinstance(fn, _ast.Attribute):
                called.add(fn.attr)
    solver_names = {"brute_force", "solve", "solver", "brute_force_sat",
                    "brute_force_vertex_cover", "product", "combinations"}
    check(not (imported & solver_names) and not (called & solver_names),
          f"reduce.py references a brute-force solver: imports={imported}, calls={called}")

    # Polynomial growth check: clause count should be O(n*k + |E|).
    for n in (10, 20, 40):
        for k in (1, 3, n // 2):
            if k >= n:
                continue
            edges = [[i, i + 1] for i in range(n - 1)]
            inst = {"n": n, "edges": edges, "k": k}
            red = reduce_mod.reduce(inst)
            bound = len(edges) + 5 * n * k + 10
            check(len(red["clauses"]) <= bound,
                  f"polynomial size n={n} k={k}: {len(red['clauses'])} > {bound}")

    print()
    print(f"tests_run={TESTS_RUN} tests_passed={TESTS_PASSED}")
    if FAILURES:
        print(f"{len(FAILURES)} failures, first few:")
        for f in FAILURES[:20]:
            print("  ", f)

    verdict = {
        "verified": TESTS_RUN > 0 and TESTS_PASSED == TESTS_RUN,
        "tests_run": TESTS_RUN,
        "tests_passed": TESTS_PASSED,
    }
    import json
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)
    return 0 if verdict["verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
