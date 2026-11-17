import random
from problems import SubsetSum, Partition
from reduce import reduce

def test_random_instances(num_trials=200, max_scale=4):
    rng = random.Random(0)
    passed = 0
    total = 0
    for _ in range(num_trials):
        scale = rng.randint(0, max_scale)
        instance = SubsetSum.random_instance(rng, scale)
        # ensure instance is valid
        SubsetSum.validate(instance)
        src_yes = SubsetSum.is_yes(instance)
        reduced = reduce(instance)
        Partition.validate(reduced)
        tgt_yes = Partition.is_yes(reduced)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch!", instance, reduced, src_yes, tgt_yes)
        total += 1
    return passed, total

if __name__ == "__main__":
    passed, total = test_random_instances()
    print(f"Passed {passed}/{total} random tests")
