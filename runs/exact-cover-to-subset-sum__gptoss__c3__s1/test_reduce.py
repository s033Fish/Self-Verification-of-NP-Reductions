import random
from problems import ExactCover, SubsetSum
from reduce import reduce

def test_random_small_instances():
    rng = random.Random(0)
    # test several scales
    for scale in range(0, 5):
        # generate a number of random instances per scale
        for _ in range(50):
            inst = ExactCover.random_instance(rng, scale)
            # ensure instance is valid
            ExactCover.validate(inst)
            reduced = reduce(inst)
            SubsetSum.validate(reduced)
            assert ExactCover.is_yes(inst) == SubsetSum.is_yes(reduced)

def test_enumerate_small_instances():
    # enumerate all exact cover instances up to small scale (universe <=3)
    for scale in range(0, 4):
        for inst in ExactCover.enumerate_instances(scale):
            reduced = reduce(inst)
            assert ExactCover.is_yes(inst) == SubsetSum.is_yes(reduced)

if __name__ == "__main__":
    test_random_small_instances()
    test_enumerate_small_instances()
    print("All tests passed")
