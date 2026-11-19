import random
from problems import OneInThreeSat, SubsetSum
from reduce import reduce

def test_random_instances(num_trials=200, scale=3):
    rng = random.Random(0)
    for _ in range(num_trials):
        instance = OneInThreeSat.random_instance(rng, scale)
        # Validate source
        OneInThreeSat.validate(instance)
        reduced = reduce(instance)
        # Validate target
        SubsetSum.validate(reduced)
        src_ans = OneInThreeSat.is_yes(instance)
        tgt_ans = SubsetSum.is_yes(reduced)
        assert src_ans == tgt_ans, f"Mismatch on {instance} -> {reduced}"

if __name__ == "__main__":
    test_random_instances()
    print("All tests passed")
