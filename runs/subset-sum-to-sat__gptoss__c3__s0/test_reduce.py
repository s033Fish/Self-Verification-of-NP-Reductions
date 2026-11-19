import random
import sys
from problems import SubsetSum, Sat
from reduce import reduce

def check_instance(inst):
    src_yes = SubsetSum.is_yes(inst)
    sat_inst = reduce(inst)
    # validate SAT instance
    Sat.validate(sat_inst)
    sat_yes = Sat.is_yes(sat_inst)
    if src_yes != sat_yes:
        print('Mismatch!')
        print('SubsetSum instance:', inst)
        print('Reduced SAT instance:', sat_inst)
        print('SubsetSum answer:', src_yes)
        print('SAT answer:', sat_yes)
        sys.exit(1)

def main():
    rng = random.Random(0)
    tests = 0
    # Edge cases
    edge_cases = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 1},
        {"numbers": [5, 7], "target": 0},
        {"numbers": [5, 7], "target": -3},
        {"numbers": [1,2,3], "target": 5},
    ]
    for inst in edge_cases:
        SubsetSum.validate(inst)
        check_instance(inst)
        tests += 1

    # Random small instances
    for scale in range(1, 5):
        for _ in range(50):
            inst = SubsetSum.random_instance(rng, scale)
            check_instance(inst)
            tests += 1
    print('All tests passed:', tests)
    # Write verdict
    import json
    with open('verdict.json', 'w') as f:
        json.dump({"verified": True, "tests_run": tests, "tests_passed": tests}, f)

if __name__ == '__main__':
    main()
