import random
import itertools
import json
from problems import ThreeSat, ExactCover
from reduce import reduce


def solve_three_sat_bruteforce(instance):
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Edge case: no clauses -> satisfiable
    if not clauses:
        return True
    for assignment in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = assignment[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_exact_cover_bruteforce(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    elements = set(range(u))
    # Simple backtrack: try all subsets of sets
    n = len(sets)
    for r in range(n+1):
        for combo in itertools.combinations(range(n), r):
            covered = set()
            disjoint = True
            for idx in combo:
                s = set(sets[idx])
                if covered & s:
                    disjoint = False
                    break
                covered |= s
            if disjoint and covered == elements:
                return True
    return False


def random_three_sat_instance(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    # ensure if there are clauses then m>=3 per spec, but we can allow smaller for testing
    if m < 3:
        # allow no clauses only
        return {"num_vars": m, "clauses": []}
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        vars_in_clause = random.sample(range(1, m+1), 3)
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
    for i in range(tests):
        inst = random_three_sat_instance()
        # validate source
        ThreeSat.validate(inst)
        red = reduce(inst)
        ExactCover.validate(red)
        ans_src = solve_three_sat_bruteforce(inst)
        ans_tgt = solve_exact_cover_bruteforce(red)
        if ans_src == ans_tgt:
            passed += 1
        else:
            print("Mismatch!", inst, red, ans_src, ans_tgt)
            break
    # also test some explicit edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1,2,3]]},
        {"num_vars": 3, "clauses": [[1,2,3], [-1,-2,-3]]},
    ]
    for inst in edge_cases:
        ThreeSat.validate(inst)
        red = reduce(inst)
        ExactCover.validate(red)
        if solve_three_sat_bruteforce(inst) != solve_exact_cover_bruteforce(red):
            print("Edge mismatch", inst, red)
            break
        else:
            passed += 1
    total = tests + len(edge_cases)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
