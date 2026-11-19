import random
from problems import ExactCover, SubsetSum
from reduce import reduce

def test_random_instances(num_trials=200):
    rng = random.Random(0)
    passed = 0
    for scale in range(0, 5):  # small universe sizes
        for _ in range(num_trials):
            inst = ExactCover.random_instance(rng, scale)
            # Validate
            ExactCover.validate(inst)
            src_yes = ExactCover.is_yes(inst)
            red = reduce(inst)
            SubsetSum.validate(red)
            tgt_yes = SubsetSum.is_yes(red)
            assert src_yes == tgt_yes, (inst, red, src_yes, tgt_yes)
            passed += 1
    print("All", passed, "random tests passed")

if __name__ == "__main__":
    test_random_instances()
