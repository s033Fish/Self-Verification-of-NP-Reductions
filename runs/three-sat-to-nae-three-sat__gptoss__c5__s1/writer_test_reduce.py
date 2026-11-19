import random
import sys
from typing import List, Dict

from problems import ThreeSat, NaeThreeSat
from reduce import reduce, _solve_3sat, _solve_naesat


def generate_random_instance(num_vars: int, max_clauses: int = 3) -> Dict:
    # generate a random list of clauses respecting ThreeSat constraints
    clauses: List[List[int]] = []
    for _ in range(random.randint(0, max_clauses)):
        # pick 3 distinct variables
        vars = random.sample(range(1, num_vars + 1), 3)
        clause = []
        for v in vars:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": num_vars, "clauses": clauses}


def test_instance(instance: Dict) -> bool:
    # validate source
    ThreeSat.validate(instance)
    # compute reduction
    red = reduce(instance)
    NaeThreeSat.validate(red)
    # compare answers
    ans_src = _solve_3sat(instance)
    ans_red = _solve_naesat(red)
    return ans_src == ans_red


def main():
    random.seed(0)
    total = 0
    passed = 0
    # test edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
        {"num_vars": 4, "clauses": [[1, -2, 3], [ -1, 2, -4], [4, -3, 2]]},
    ]
    for inst in edge_cases:
        total += 1
        if test_instance(inst):
            passed += 1
        else:
            print("Failed on edge case", inst)
            sys.exit(1)
    # random tests
    for num_vars in range(0, 5):
        # ensure at least 3 vars if we generate clauses
        for _ in range(40):
            if num_vars < 3:
                # only allow empty clause list for <3 vars
                instance = {"num_vars": num_vars, "clauses": []}
            else:
                instance = generate_random_instance(num_vars)
            total += 1
            if test_instance(instance):
                passed += 1
            else:
                print("Failed on instance", instance)
                sys.exit(1)
    # write verdict
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    import json, pathlib
    pathlib.Path('verdict.json').write_text(json.dumps(verdict))
    print(json.dumps(verdict))
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
