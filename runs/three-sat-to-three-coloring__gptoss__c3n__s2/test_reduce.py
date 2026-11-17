import random
import json
from typing import List, Dict

from problems import ThreeSat, ThreeColoring
import reduce

def solve_3sat(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
                if lit > 0 and val == 1:
                    clause_ok = True
                if lit < 0 and val == 0:
                    clause_ok = True
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def solve_3coloring(instance: Dict) -> bool:
    """Backtracking 3‑colorability solver for small graphs."""
    n = instance["n"]
    edges = [(u, v) for u, v in instance["edges"]]
    adj: List[List[int]] = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    colors = [-1] * n
    def backtrack(v: int) -> bool:
        if v == n:
            return True
        for c in range(3):
            conflict = any(colors[nb] == c for nb in adj[v])
            if conflict:
                continue
            colors[v] = c
            if backtrack(v + 1):
                return True
            colors[v] = -1
        return False
    return backtrack(0)

def random_3sat(m: int, num_clauses: int) -> Dict:
    clauses = []
    for _ in range(num_clauses):
        vars = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars:
            clause.append(v if random.choice([True, False]) else -v)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests() -> Dict:
    tests_run = 0
    tests_passed = 0
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 3, "clauses": [[1, 2, 3], [-1, -2, -3]]},
    ]
    for inst in edge_cases:
        tests_run += 1
        ThreeSat.validate(inst)
        reduced = reduce.reduce(inst)
        ThreeColoring.validate(reduced)
        sat = solve_3sat(inst)
        col = solve_3coloring(reduced)
        if sat == col:
            tests_passed += 1
        else:
            print("FAIL edge case", inst, sat, col)
    for _ in range(50):
        m = random.randint(0, 4)
        max_clauses = 5
        num_clauses = random.randint(0, max_clauses)
        if num_clauses > 0 and m < 3:
            m = 3
        inst = random_3sat(m, num_clauses)
        tests_run += 1
        ThreeSat.validate(inst)
        reduced = reduce.reduce(inst)
        ThreeColoring.validate(reduced)
        sat = solve_3sat(inst)
        col = solve_3coloring(reduced)
        if sat == col:
            tests_passed += 1
        else:
            print("FAIL random", inst, sat, col)
    return {"tests_run": tests_run, "tests_passed": tests_passed}

if __name__ == "__main__":
    result = run_tests()
    verified = result["tests_run"] == result["tests_passed"]
    verdict = {"verified": verified, "tests_run": result["tests_run"], "tests_passed": result["tests_passed"]}
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
