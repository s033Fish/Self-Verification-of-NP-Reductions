import itertools
import random

from problems import DominatingSet, Sat
from reduce import reduce


# ---------------- brute force dominating set ----------------

def solve_dominating_set(inst):
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
    vertices = list(range(n))
    for size in range(0, min(k, n) + 1):
        for combo in itertools.combinations(vertices, size):
            chosen = set(combo)
            if all(v in chosen or (adj[v] & chosen) for v in vertices):
                return True
    return False


# ---------------- DPLL SAT solver ----------------

def solve_sat(inst):
    m = inst["num_vars"]
    clauses = [list(c) for c in inst["clauses"]]

    def simplify(clauses, lit):
        """Assign lit=True, return simplified clause list or None if conflict."""
        out = []
        for c in clauses:
            if lit in c:
                continue
            nc = [x for x in c if x != -lit]
            if not nc:
                return None
            out.append(nc)
        return out

    def dpll(clauses):
        if not clauses:
            return True
        if any(len(c) == 0 for c in clauses):
            return False
        # unit propagation
        while True:
            unit = None
            for c in clauses:
                if len(c) == 1:
                    unit = c[0]
                    break
            if unit is None:
                break
            clauses = simplify(clauses, unit)
            if clauses is None:
                return False
        if not clauses:
            return True
        # pure literal
        lits = set(l for c in clauses for l in c)
        for l in list(lits):
            if -l not in lits:
                clauses = simplify(clauses, l)
                if clauses is None:
                    return False
        if not clauses:
            return True
        # choose shortest clause literal
        c = min(clauses, key=len)
        lit = c[0]
        for choice in (lit, -lit):
            nc = simplify(clauses, choice)
            if nc is not None and dpll(nc):
                return True
        return False

    return dpll(clauses)


# ---------------- instance generators ----------------

def random_dominating_instance(rng, max_n=7, max_k=7):
    n = rng.randint(0, max_n)
    possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
    rng.shuffle(possible)
    m = rng.randint(0, len(possible))
    edges = [list(e) for e in possible[:m]]
    k = rng.randint(-2, max_k)
    return {"n": n, "edges": edges, "k": k}


def main():
    rng = random.Random(12345)
    tests_run = 0
    tests_passed = 0

    instances = []

    # Explicit edge cases.
    instances += [
        {"n": 0, "edges": [], "k": 0},
        {"n": 0, "edges": [], "k": 5},
        {"n": 0, "edges": [], "k": -1},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 1},
        {"n": 3, "edges": [], "k": 2},   # 3 isolated, need 3
        {"n": 3, "edges": [], "k": 3},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 1},
        {"n": 4, "edges": [[0, 1], [1, 2], [2, 3]], "k": 2},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": 2},
        {"n": 5, "edges": [[0, 1], [2, 3]], "k": 3},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 3},
        {"n": 6, "edges": [[0, 1], [2, 3], [4, 5]], "k": 2},
    ]

    for _ in range(600):
        instances.append(random_dominating_instance(rng))

    for inst in instances:
        DominatingSet.validate(inst)
        expected = solve_dominating_set(inst)
        red = reduce(inst)
        Sat.validate(red)
        got = solve_sat(red)
        tests_run += 1
        if expected == got:
            tests_passed += 1
        else:
            print("MISMATCH", inst, "expected", expected, "got", got, "red", red)

    print(f"tests_run={tests_run} tests_passed={tests_passed}")
    assert tests_run == tests_passed, "some tests failed"


if __name__ == "__main__":
    main()
