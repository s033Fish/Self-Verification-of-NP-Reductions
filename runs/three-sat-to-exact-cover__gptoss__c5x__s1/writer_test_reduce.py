import random
from typing import List, Dict, Any

from problems import ThreeSat, ExactCover
from reduce import reduce


def solve_three_sat(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for assign in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (assign >> var) & 1
                lit_true = (val == 1) if lit > 0 else (val == 0)
                if lit_true:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover(instance: Dict[str, Any]) -> bool:
    u = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    n = len(sets)
    # brute force over subsets of sets
    for mask in range(1 << n):
        covered = [0] * u
        valid = True
        for i in range(n):
            if (mask >> i) & 1:
                for e in sets[i]:
                    covered[e] += 1
                    if covered[e] > 1:
                        valid = False
                        break
                if not valid:
                    break
        if not valid:
            continue
        if all(c == 1 for c in covered):
            return True
    return False


def random_three_sat(max_vars=4, max_clauses=5) -> Dict[str, Any]:
    m = random.randint(0, max_vars)
    # ensure at least 3 vars if there are clauses
    if m < 3:
        # allow empty clause list
        clauses = []
        return {"num_vars": m, "clauses": clauses}
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        vars_in_clause = random.sample(range(1, m + 1), 3)
        clause = []
        for v in vars_in_clause:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    random.seed(0)
    tests = 200
    passed = 0
    for _ in range(tests):
        inst = random_three_sat()
        # validate
        ThreeSat.validate(inst)
        red = reduce(inst)
        ExactCover.validate(red)
        ans1 = solve_three_sat(inst)
        ans2 = solve_exact_cover(red)
        if ans1 == ans2:
            passed += 1
        else:
            print("Mismatch!", inst, red, ans1, ans2)
            break
    # Edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
    ]
    for inst in edge_cases:
        ThreeSat.validate(inst)
        red = reduce(inst)
        ExactCover.validate(red)
        if solve_three_sat(inst) != solve_exact_cover(red):
            print("Edge mismatch", inst, red)
            break
        else:
            passed += 1
    total = tests + len(edge_cases)
    print(f"Tests run: {total}, passed: {passed}")
    # write verdict
    import json
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
