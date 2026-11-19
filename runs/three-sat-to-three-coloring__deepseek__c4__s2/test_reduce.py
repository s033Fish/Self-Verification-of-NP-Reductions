import itertools, random, sys
from problems import ThreeSat, ThreeColoring
from reduce import reduce

def sat_solve(inst):
    m = inst["num_vars"]; clauses = inst["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for cl in clauses:
            if not any((bits[abs(l)-1] if l > 0 else not bits[abs(l)-1]) for l in cl):
                ok = False; break
        if ok: return True
    return True  # no clauses -> True (loop over 2^0 = one empty assignment)

def col_solve(inst):
    n = inst["n"]; edges = inst["edges"]
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    colors = [-1] * n
    def bt(v):
        if v == n: return True
        for c in range(3):
            if all(colors[u] != c for u in adj[v]):
                colors[v] = c
                if bt(v + 1): return True
                colors[v] = -1
        return False
    return bt(0)

def random_sat(rng, max_vars=5, max_clauses=6):
    m = rng.randint(0, max_vars)
    clauses = []
    for _ in range(rng.randint(0, max_clauses)):
        if m < 3: break
        vs = rng.sample(range(1, m + 1), 3)
        cl = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(cl)
    return {"num_vars": m, "clauses": clauses}

def main():
    rng = random.Random(12345)
    tests = 0; passed = 0

    # explicit edge cases
    cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 1, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3], [1, -2, 3], [-1, 2, -3]]},
        {"num_vars": 4, "clauses": [[1, 2, 3], [-1, -2, 3], [1, -2, -3], [-1, 2, -3]]},
    ]
    for _ in range(400):
        cases.append(random_sat(rng))

    for inst in cases:
        ThreeSat.validate(inst)
        out = reduce(inst)
        ThreeColoring.validate(out)
        a = sat_solve(inst)
        b = col_solve(out)
        tests += 1
        if a == b:
            passed += 1
        else:
            print("MISMATCH", inst, "->", out, "sat=", a, "col=", b)

    print(f"tests={tests} passed={passed}")
    return 0 if passed == tests else 1

if __name__ == "__main__":
    sys.exit(main())
