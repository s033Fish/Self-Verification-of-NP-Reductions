import random
import json
from problems import SubsetSum, Sat
from reduce import reduce


def subset_sum_bruteforce(instance):
    SubsetSum.validate(instance)
    nums = instance['numbers']
    target = instance['target']
    n = len(nums)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask & (1 << i):
                s += nums[i]
        if s == target:
            return True
    return False


def sat_bruteforce(instance):
    Sat.validate(instance)
    m = instance['num_vars']
    clauses = instance['clauses']
    for cl in clauses:
        if len(cl) == 0:
            return False
    for assign in range(1 << m):
        ok = True
        for cl in clauses:
            clause_sat = False
            for lit in cl:
                var = abs(lit) - 1
                val = bool(assign & (1 << var))
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


def generate_random_instance(max_len=3, max_val=3, target_range=(-5, 5)):
    """Generate a small random Subset‑Sum instance.

    The parameters are deliberately tiny so that the SAT instance produced
    by the reduction has at most a few dozen variables, keeping the brute‑
    force SAT checker tractable.
    """
    length = random.randint(0, max_len)
    numbers = [random.randint(0, max_val) for _ in range(length)]
    target = random.randint(*target_range)
    return {"numbers": numbers, "target": target}


def run_tests(num_tests=200):
    passed = 0
    for _ in range(num_tests):
        inst = generate_random_instance()
        ss_ans = subset_sum_bruteforce(inst)
        sat_inst = reduce(inst)
        sat_ans = sat_bruteforce(sat_inst)
        if ss_ans == sat_ans:
            passed += 1
        else:
            print('FAIL')
            print('SubsetSum instance:', inst)
            print('SubsetSum answer:', ss_ans)
            print('Reduced SAT instance:', sat_inst)
            print('SAT answer:', sat_ans)
            break
    return passed, num_tests

if __name__ == '__main__':
    passed, total = run_tests(300)
    result = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
