import json
from problems import SubsetSum, Partition
from reduce import reduce


def run_tests():
    tests_run = 0
    tests_passed = 0
    # Test a variety of small instances
    for instance in SubsetSum.enumerate_instances(scale=3):
        # limit numbers size to keep enumeration reasonable (already small)
        reduced = reduce(instance)
        source_yes = SubsetSum.is_yes(instance)
        target_yes = Partition.is_yes(reduced)
        tests_run += 1
        if source_yes == target_yes:
            tests_passed += 1
        else:
            print("Mismatch!", instance, reduced, source_yes, target_yes)
            break
    # Additional edge cases
    edge_cases = [
        {"numbers": [], "target": 0},
        {"numbers": [], "target": 5},
        {"numbers": [0,0,0], "target": 0},
        {"numbers": [5,7,2], "target": -3},
        {"numbers": [1,2,3], "target": 10},
    ]
    for instance in edge_cases:
        reduced = reduce(instance)
        source_yes = SubsetSum.is_yes(instance)
        target_yes = Partition.is_yes(reduced)
        tests_run += 1
        if source_yes == target_yes:
            tests_passed += 1
        else:
            print("Mismatch edge", instance, reduced, source_yes, target_yes)
            break
    verified = tests_run == tests_passed
    result = {"verified": verified, "tests_run": tests_run, "tests_passed": tests_passed}
    with open("verdict.json", "w") as f:
        json.dump(result, f)
    print(json.dumps(result))

if __name__ == "__main__":
    run_tests()
