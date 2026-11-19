import itertools, random, json, sys
from problems import SubsetSum, Sat
from reduce import reduce

def solve_subset_sum(instance):
    numbers = instance['numbers']
    target = instance['target']
    n = len(numbers)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += numbers[i]
        if s == target:
            return True
    return False

def solve_sat(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for cl in clauses:
        if len(cl) == 0:
            return False
    for assign in itertools.product([False, True], repeat=m):
        ok = True
        for cl in clauses:
            clause_sat = False
            for lit in cl:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                ok = False
                break
        if ok:
            return True
    return False

def random_instance():
    """Generate a tiny Subset‑Sum instance.
    To keep the SAT instance tractable for the exhaustive SAT solver we
    bound the target to at most 5 and the number of elements to at most 3.
    """
    n = random.randint(0, 3)
    numbers = [random.randint(0, 5) for _ in range(n)]
    max_target = min(5, sum(numbers))
    target = random.randint(-3, max_target)
    return {"numbers": numbers, "target": target}

def main():
    tests = 200
    passed = 0
    for _ in range(tests):
        src = random_instance()
        SubsetSum.validate(src)
        sat_inst = reduce(src)
        Sat.validate(sat_inst)
        src_ans = solve_subset_sum(src)
        sat_ans = solve_sat(sat_inst)
        if src_ans == sat_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('src', src)
            print('sat', sat_inst)
            print('src_ans', src_ans, 'sat_ans', sat_ans)
            sys.exit(1)
    verdict = {
        "verified": passed == tests,
        "tests_run": tests,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('All tests passed', passed, '/', tests)

if __name__ == '__main__':
    main()
