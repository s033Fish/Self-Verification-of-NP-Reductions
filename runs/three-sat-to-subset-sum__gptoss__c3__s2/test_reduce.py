import json
from problems import ThreeSat, SubsetSum
from reduce import reduce

def run_tests():
    total = 0
    passed = 0
    # Enumerate all small 3-SAT instances up to scale 3 (as doc suggests)
    for instance in ThreeSat.enumerate_instances(scale=3):
        total += 1
        # original answer
        ans_original = ThreeSat.is_yes(instance)
        # reduction
        reduced = reduce(instance)
        # validate reduced instance (should not raise)
        SubsetSum.validate(reduced)
        ans_reduced = SubsetSum.is_yes(reduced)
        if ans_original == ans_reduced:
            passed += 1
        else:
            print("Mismatch!", instance, ans_original, reduced, ans_reduced)
    # Additional edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 5, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
    ]
    for instance in edge_cases:
        total += 1
        ans_original = ThreeSat.is_yes(instance)
        reduced = reduce(instance)
        SubsetSum.validate(reduced)
        ans_reduced = SubsetSum.is_yes(reduced)
        if ans_original == ans_reduced:
            passed += 1
        else:
            print("Mismatch edge", instance, ans_original, reduced, ans_reduced)
    # write verdict
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    run_tests()
