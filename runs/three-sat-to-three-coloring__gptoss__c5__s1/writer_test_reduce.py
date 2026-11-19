import random
import itertools
import json
from problems import ThreeSat, ThreeColoring
from reduce import reduce


def brute_sat(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            lit_true = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0:
                    lit_true = lit_true or val
                else:
                    lit_true = lit_true or (not val)
                if lit_true:
                    break
            if not lit_true:
                ok = False
                break
        if ok:
            return True
    return False


def brute_coloring(instance):
    """Backtracking search for a proper 3‑coloring.

    The naive exhaustive search quickly becomes infeasible for the graphs
    produced by the reduction (up to a few dozen vertices).  This implementation
    assigns colours recursively and aborts early when a conflict is detected.
    """
    n = instance["n"]
    adj: list[set[int]] = [set() for _ in range(n)]
    for u, v in instance["edges"]:
        adj[u].add(v)
        adj[v].add(u)

    colors = [-1] * n

    def backtrack(v: int) -> bool:
        if v == n:
            return True
        for c in range(3):
            conflict = any(colors[nb] == c for nb in adj[v] if colors[nb] != -1)
            if conflict:
                continue
            colors[v] = c
            if backtrack(v + 1):
                return True
            colors[v] = -1
        return False

    return backtrack(0)


def random_sat_instance(max_vars=4, max_clauses=5):
    """Generate a random 3‑SAT instance respecting the problem constraints.

    If we generate any clauses we ensure there are at least three variables so
    that each clause can pick three distinct variables.
    """
    m = random.randint(0, max_vars)
    if m >= 3:
        num_clauses = random.randint(0, max_clauses)
    else:
        num_clauses = 0
    clauses = []
    for _ in range(num_clauses):
        vars_chosen = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_chosen:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def run_tests(num_tests=200):
    passed = 0
    for i in range(num_tests):
        sat_inst = random_sat_instance()
        ThreeSat.validate(sat_inst)
        graph_inst = reduce(sat_inst)
        ThreeColoring.validate(graph_inst)
        sat_ans = brute_sat(sat_inst)
        col_ans = brute_coloring(graph_inst)
        if sat_ans == col_ans:
            passed += 1
        else:
            print("Mismatch on test", i)
            print("SAT instance", sat_inst)
            print("Graph", graph_inst)
            print("SAT ans", sat_ans, "Color ans", col_ans)
            break
    return passed, num_tests

if __name__ == "__main__":
    passed, total = run_tests()
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(result))
    with open("verdict.json", "w") as f:
        json.dump(result, f)
