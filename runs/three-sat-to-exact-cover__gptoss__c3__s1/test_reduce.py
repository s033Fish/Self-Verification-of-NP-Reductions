import random
from problems import ThreeSat, ExactCover
from reduce import reduce

def test_all_small_instances():
    # enumerate all instances with num_vars <= 3 (scale 3)
    for instance in ThreeSat.enumerate_instances(3):
        # validate (should be valid)
        ThreeSat.validate(instance)
        reduced = reduce(instance)
        ExactCover.validate(reduced)
        assert ThreeSat.is_yes(instance) == ExactCover.is_yes(reduced), f"Mismatch on {instance}"

def test_random_instances():
    rng = random.Random(0)
    for scale in range(0, 5):
        for _ in range(20):
            instance = ThreeSat.random_instance(rng, scale)
            ThreeSat.validate(instance)
            reduced = reduce(instance)
            ExactCover.validate(reduced)
            assert ThreeSat.is_yes(instance) == ExactCover.is_yes(reduced), f"Mismatch on random {instance}"

if __name__ == "__main__":
    test_all_small_instances()
    test_random_instances()
    print("All tests passed")
