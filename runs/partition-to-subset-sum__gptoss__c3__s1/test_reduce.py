import json
import random
from problems import Partition, SubsetSum
from reduce import reduce


def run_tests(num_trials: int = 200) -> tuple[int, int]:
    total = 0
    passed = 0
    for i in range(num_trials):
        rng = random.Random(i)
        # Choose a small scale (0 to 6 numbers) for exhaustive brute force
        scale = rng.randint(0, 6)
        instance = Partition.random_instance(rng, scale)
        # Ensure instance is valid (should be by generator)
        Partition.validate(instance)
        expected = Partition.is_yes(instance)
        reduced = reduce(instance)
        # Validate reduced instance for SubsetSum
        SubsetSum.validate(reduced)
        actual = SubsetSum.is_yes(reduced)
        total += 1
        if expected == actual:
            passed += 1
        else:
            # For debugging, you could print the failing case
            print("FAIL", instance, reduced, expected, actual)
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests(500)
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict, indent=2))
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
