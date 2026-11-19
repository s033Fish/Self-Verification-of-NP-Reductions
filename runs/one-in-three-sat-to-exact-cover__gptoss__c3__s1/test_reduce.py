import random
from problems import OneInThreeSat, ExactCover
from reduce import reduce

def test_all_small(scale=3):
    count = 0
    for inst in OneInThreeSat.enumerate_instances(scale):
        reduced = reduce(inst)
        # validate reduced
        ExactCover.validate(reduced)
        assert ExactCover.is_yes(reduced) == OneInThreeSat.is_yes(inst)
        count += 1
    return count

def test_random_trials(trials=100, max_vars=5):
    rng = random.Random(0)
    for _ in range(trials):
        scale = rng.randint(0, max_vars)
        inst = OneInThreeSat.random_instance(rng, scale)
        reduced = reduce(inst)
        ExactCover.validate(reduced)
        assert ExactCover.is_yes(reduced) == OneInThreeSat.is_yes(inst)

if __name__ == "__main__":
    total = test_all_small(3)
    print("tested", total, "small instances")
    test_random_trials()
    print("random tests passed")
