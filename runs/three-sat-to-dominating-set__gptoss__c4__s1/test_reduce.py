import itertools
import random
import json
from problems import ThreeSat, DominatingSet
from reduce import reduce


def solve_three_sat(inst):
    m = inst["num_vars"]
    clauses = inst["clauses"]
    # iterate all assignments
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    sat = True
                    break
                if lit < 0 and not val:
                    sat = True
                    break
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False


def solve_dominating_set(inst):
    n = inst["n"]
    edges = inst["edges"]
    k = inst["k"]
    if k < 0:
        return False
    if n == 0:
        return True
    if k >= n:
        return True
    # adjacency list including self
    adj = [set([i]) for i in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    # check subsets up to k
    vertices = list(range(n))
    for r in range(k + 1):
        for combo in itertools.combinations(vertices, r):
            dominated = set()
            for v in combo:
                dominated.update(adj[v])
            if len(dominated) == n:
                return True
    return False


def random_three_sat(m, clause_count):
    # generate random clauses respecting 3 distinct vars
    clauses = []
    vars_list = list(range(1, m+1))
    for _ in range(clause_count):
        vars_in = random.sample(vars_list, 3)
        clause = []
        for v in vars_in:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_trials=200):
    for _ in range(num_trials):
        # random small instance
        m = random.randint(0, 4)
        # ensure if clauses exist, m>=3 per spec, but we can still test regardless
        max_clauses = 5
        clause_count = random.randint(0, max_clauses)
        # If clause_count>0 and m<3, set m=3 to be valid
        if clause_count > 0 and m < 3:
            m = 3
        inst = random_three_sat(m, clause_count)
        # validate
        ThreeSat.validate(inst)
        # reduce
        red = reduce(inst)
        # solve both
        sat = solve_three_sat(inst)
        dom = solve_dominating_set(red)
        if sat != dom:
            print("Mismatch!", inst, red, sat, dom)
            return False
    return True

if __name__ == "__main__":
    ok = run_tests(500)
    verdict = {
        "verified": ok,
        "tests_run": 500,
        "tests_passed": 500 if ok else 0,
    }
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
