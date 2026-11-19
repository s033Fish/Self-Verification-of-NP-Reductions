import random
import sys
from problems import ThreeSat, IndependentSet
from reduce import reduce

def test_all_small():
    # Enumerate all 3-SAT instances with up to 3 variables (scale=3)
    count = 0
    for instance in ThreeSat.enumerate_instances(scale=3):
        # Only consider valid instances (enumerate ensures that)
        reduced = reduce(instance)
        # Validate target instance
        IndependentSet.validate(reduced)
        yes_src = ThreeSat.is_yes(instance)
        yes_tgt = IndependentSet.is_yes(reduced)
        if yes_src != yes_tgt:
            print("Mismatch!", instance, reduced, yes_src, yes_tgt)
            return False
        count += 1
    print("All small instances passed:", count)
    return True

def test_random():
    rng = random.Random(0)
    for scale in range(0, 6):  # variables from 0 to 5
        for _ in range(20):
            inst = ThreeSat.random_instance(rng, scale)
            reduced = reduce(inst)
            IndependentSet.validate(reduced)
            if ThreeSat.is_yes(inst) != IndependentSet.is_yes(reduced):
                print("Random mismatch", inst, reduced)
                return False
    print("Random tests passed")
    return True

if __name__ == "__main__":
    ok = test_all_small() and test_random()
    sys.exit(0 if ok else 1)
