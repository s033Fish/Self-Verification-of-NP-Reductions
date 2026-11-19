import json
import random
from problems import ExactCover, SubsetSum
from reduce import reduce

random.seed(0)

def run_tests(num_random=200, max_scale=4):
    passed = 0
    total = 0
    # enumerate all small instances up to max_scale
    for scale in range(max_scale + 1):
        for instance in ExactCover.enumerate_instances(scale):
            total += 1
            reduced = reduce(instance)
            yes_original = ExactCover.is_yes(instance)
            yes_reduced = SubsetSum.is_yes(reduced)
            if yes_original == yes_reduced:
                passed += 1
            else:
                print("Mismatch!", instance, reduced, yes_original, yes_reduced)
                return total, passed
    # also random instances
    for _ in range(num_random):
        scale = random.randint(0, max_scale)
        instance = ExactCover.random_instance(random, scale)
        total += 1
        reduced = reduce(instance)
        yes_original = ExactCover.is_yes(instance)
        yes_reduced = SubsetSum.is_yes(reduced)
        if yes_original == yes_reduced:
            passed += 1
        else:
            print("Random mismatch!", instance, reduced, yes_original, yes_reduced)
            return total, passed
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
