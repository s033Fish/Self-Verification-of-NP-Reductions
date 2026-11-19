"""Independent brute-force check of reduce.py (DominatingSet -> SAT)."""
from itertools import combinations, product
import random

from problems import DominatingSet, Sat
from reduce import reduce


# ---------------- brute force solvers ----------------

def solve_dominating(inst):
    n = inst["n"]
    edges = inst["edges"]
    k = inst["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    closed = [adj[i] | {i} for i in range(n)]
    for size in range(0, min(k, n) + 1):
        for comb in combinations(range(n), size):
            covered = set()
            for c in comb:
                covered |= closed[c]
            if len(covered) == n:
                return True
    return False


def solve_sat(inst):
    """DPLL SAT solver (sound and complete)."""
    m = inst["num_vars"]
    clauses = [frozenset(c) for c in inst["clauses"]]
    if any(len(c) == 0 for c in clauses):
        return False

    def dpll(clauses, assign):
        # unit propagation, processing every clause
        while True:
            new = []
            unit = None
            for c in clauses:
                if any(lit in assign for lit in c):
                    continue
                rem = frozenset(l for l in c if -l not in assign)
                if not rem:
                    return False
                if len(rem) == 1 and unit is None:
                    unit = next(iter(rem))
                new.append(rem)
            if unit is None:
                clauses = new
                break
            assign = assign | {unit}
            clauses = new
        if not clauses:
            return True
        # choose a literal
        lit = next(iter(clauses[0]))
        return dpll(clauses, assign | {lit}) or dpll(clauses, assign | {-lit})

    return dpll(clauses, frozenset())


# ---------------- instance generators ----------------

def all_graphs(n):
    pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    for mask in range(1 << len(pairs)):
        edges = [list(pairs[i]) for i in range(len(pairs)) if mask >> i & 1]
        yield {"n": n, "edges": edges}


def random_graph(n, rng):
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < 0.4:
                edges.append([u, v])
    return {"n": n, "edges": edges}


def main():
    tests = 0
    passed = 0
    failures = []

    def check(inst):
        nonlocal tests, passed
        tests += 1
        DominatingSet.validate(inst)
        red = reduce(inst)
        Sat.validate(red)
        a = solve_dominating(inst)
        b = solve_sat(red)
        if a == b:
            passed += 1
        else:
            failures.append((inst, red, a, b))

    # exhaustive small graphs, all k in a wide range
    for n in range(0, 6):
        for g in all_graphs(n):
            for k in range(-1, n + 3):
                inst = {"n": g["n"], "edges": g["edges"], "k": k}
                check(inst)

    # random slightly larger
    rng = random.Random(12345)
    for _ in range(400):
        n = rng.randint(0, 9)
        g = random_graph(n, rng)
        k = rng.randint(-1, n + 2)
        check({"n": g["n"], "edges": g["edges"], "k": k})

    # larger graphs but small k (keeps the SAT encoding small)
    rng = random.Random(777)
    for _ in range(300):
        n = rng.randint(6, 14)
        g = random_graph(n, rng)
        for k in range(0, 4):
            check({"n": g["n"], "edges": g["edges"], "k": k})

    # k = 0 and k = 1 on random graphs of moderate size
    rng = random.Random(2024)
    for _ in range(300):
        n = rng.randint(0, 12)
        g = random_graph(n, rng)
        for k in (-1, 0, 1):
            check({"n": g["n"], "edges": g["edges"], "k": k})

    print(f"tests_run={tests} tests_passed={passed}")
    if failures:
        print("FAILURES:", len(failures))
        for f in failures[:10]:
            print(f)
    return tests, passed, failures


if __name__ == "__main__":
    main()
