"""Independent verification of reduce.py (3-SAT -> Vertex Cover).

Contains:
  * brute-force / exact solvers for both problems, written from the
    definitions in problems.py (no solvers are provided there);
  * a generator of small valid 3-SAT instances;
  * tests comparing solver answers on source instances and their reductions;
  * a cross-check of the exact Vertex Cover solver against a naive brute
    force, and exhaustive small-formula coverage.

Running this module prints a summary and writes verdict.json.
"""
import itertools
import json
import random
import sys

from problems import SOURCE, TARGET
from reduce import reduce


# --------------------------------------------------------------------------
# Solvers written directly from the problem definitions.
# --------------------------------------------------------------------------

def sat_solve(instance):
    """True iff some assignment satisfies every clause (brute force)."""
    SOURCE.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            if not any((bits[abs(l) - 1] if l > 0 else not bits[abs(l) - 1])
                       for l in clause):
                ok = False
                break
        if ok:
            return True
    return False


def vc_solve(instance):
    """True iff some vertex set of size <= k covers every edge.

    Exact minimum vertex cover via branch-and-bound on a maximum-degree
    vertex (include it, or exclude it and include all its neighbours).
    Complete search, written from the definition.
    """
    TARGET.validate(instance)
    n = instance["n"]
    edges = [tuple(e) for e in instance["edges"]]
    k = instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True

    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    memo = {}

    def rec(rem):
        # rem is a frozenset of vertices still allowed to be chosen.
        cached = memo.get(rem)
        if cached is not None:
            return cached
        best = -1
        best_deg = 0
        for v in rem:
            d = len(adj[v] & rem)
            if d > best_deg:
                best_deg = d
                best = v
        if best_deg == 0:
            memo[rem] = 0
            return 0
        v = best
        # Option 1: put v in the cover.
        opt1 = 1 + rec(rem - {v})
        # Option 2: leave v out; all its remaining neighbours must be in.
        nb = adj[v] & rem
        opt2 = len(nb) + rec(rem - {v} - nb)
        result = min(opt1, opt2)
        memo[rem] = result
        return result

    return rec(frozenset(range(n))) <= k


def vc_solve_naive(instance):
    """Reference brute force, used only to cross-check vc_solve."""
    n, edges, k = instance["n"], instance["edges"], instance["k"]
    if k < 0:
        return False
    if k >= n:
        return True
    for size in range(k + 1):
        for sub in itertools.combinations(range(n), size):
            s = set(sub)
            if all(u in s or v in s for u, v in edges):
                return True
    return False


# --------------------------------------------------------------------------
# Instance generation.
# --------------------------------------------------------------------------

def random_sat_instance(rng, max_vars=4, max_clauses=4):
    m = rng.randint(0, max_vars)
    max_clauses = max_clauses if m >= 3 else 0
    c = rng.randint(0, max_clauses)
    clauses = []
    for _ in range(c):
        vs = rng.sample(range(1, m + 1), 3)
        clause = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def all_clauses_over(vs):
    pool = set()
    for order in itertools.permutations(vs):
        for signs in itertools.product([1, -1], repeat=len(vs)):
            pool.add(tuple(s * v for s, v in zip(signs, order)))
    return [list(c) for c in sorted(pool)]


# --------------------------------------------------------------------------
# Tests.
# --------------------------------------------------------------------------

class Counter:
    def __init__(self):
        self.run = 0
        self.passed = 0
        self.failures = []

    def check(self, condition, description):
        self.run += 1
        if condition:
            self.passed += 1
        else:
            self.failures.append(description)


def run_tests():
    c = Counter()
    rng = random.Random(20240517)

    # (0) Cross-check the exact VC solver against naive brute force.
    for _ in range(1500):
        n = rng.randint(0, 7)
        pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
        rng.shuffle(pairs)
        edges = [list(e) for e in pairs[:rng.randint(0, len(pairs))]]
        inst = {"n": n, "edges": edges, "k": rng.randint(-1, n + 1)}
        TARGET.validate(inst)
        c.check(vc_solve(inst) == vc_solve_naive(inst),
                "vc solver mismatch on %r" % (inst,))

    # (1) Documented edge cases.
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        # all 8 clauses over 3 vars -> unsatisfiable
        {"num_vars": 3, "clauses": all_clauses_over([1, 2, 3])},
        # 7 of the 8 clauses -> satisfiable
        {"num_vars": 3, "clauses": all_clauses_over([1, 2, 3])[:-1]},
    ]

    # (2) Exhaustive small formulas: m = 3, up to 2 clauses (with repeats).
    pool = all_clauses_over([1, 2, 3])
    exhaustive = []
    for num_clauses in range(0, 3):
        for combo in itertools.combinations_with_replacement(pool, num_clauses):
            exhaustive.append({"num_vars": 3,
                               "clauses": [list(x) for x in combo]})

    # (3) Random formulas, several size regimes.
    random_instances = []
    for _ in range(600):
        random_instances.append(random_sat_instance(rng, max_vars=4, max_clauses=5))
    for _ in range(300):
        random_instances.append(random_sat_instance(rng, max_vars=6, max_clauses=8))

    all_instances = edge_cases + exhaustive + random_instances

    for inst in all_instances:
        try:
            red = reduce(inst)
        except Exception as exc:  # noqa: BLE001
            c.check(False, "reduce raised %r on %r" % (exc, inst))
            continue
        # The reduction must output a valid target instance.
        try:
            TARGET.validate(red)
        except Exception as exc:  # noqa: BLE001
            c.check(False, "reduced instance invalid (%r) for %r" % (exc, inst))
            continue
        src = sat_solve(inst)
        tgt = vc_solve(red)
        c.check(src == tgt,
                "answer mismatch src=%s tgt=%s for %r -> %r" % (src, tgt, inst, red))

    return c


def main():
    c = run_tests()
    print("tests_run=%d tests_passed=%d failures=%d"
          % (c.run, c.passed, len(c.failures)))
    for f in c.failures[:20]:
        print("FAIL:", f)

    verified = (c.run == c.passed and c.run > 0)
    verdict = {"verified": bool(verified),
               "tests_run": int(c.run),
               "tests_passed": int(c.passed)}
    with open("verdict.json", "w") as fh:
        json.dump(verdict, fh)
    print("verdict:", verdict)
    return 0 if verified else 1


if __name__ == "__main__":
    sys.exit(main())
