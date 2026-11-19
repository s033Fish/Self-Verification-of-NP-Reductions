import json
import random
from problems import Sat, IndependentSet
from reduce import reduce

def run_tests(num_trials=200, max_scale=4):
    rng = random.Random(0)
    total = 0
    passed = 0
    # Include some explicit edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},  # no clauses, trivially yes
        {"num_vars": 1, "clauses": [[]]},  # contains empty clause -> no
        {"num_vars": 2, "clauses": [[1, -1]]},  # tautology clause, yes
    ]
    for inst in edge_cases:
        total += 1
        sat_yes = Sat.is_yes(inst)
        ind_inst = reduce(inst)
        IndependentSet.validate(ind_inst)
        ind_yes = IndependentSet.is_yes(ind_inst)
        if sat_yes == ind_yes:
            passed += 1
        else:
            print('Mismatch on edge case', inst, sat_yes, ind_yes)
            break
    # Random tests
    for _ in range(num_trials):
        scale = rng.randint(0, max_scale)
        inst = Sat.random_instance(rng, scale)
        total += 1
        sat_yes = Sat.is_yes(inst)
        ind_inst = reduce(inst)
        IndependentSet.validate(ind_inst)
        ind_yes = IndependentSet.is_yes(ind_inst)
        if sat_yes == ind_yes:
            passed += 1
        else:
            print('Mismatch on random instance', inst, sat_yes, ind_yes)
            break
    return total, passed

if __name__ == '__main__':
    total, passed = run_tests()
    print(f'Tested {total} instances, passed {passed}')
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print('Verdict written to verdict.json')
