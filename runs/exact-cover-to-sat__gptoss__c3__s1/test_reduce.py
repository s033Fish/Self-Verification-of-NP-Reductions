import random
from problems import ExactCover, Sat
from reduce import reduce

def test_random_instances(num_tests=200, max_scale=4):
    rng = random.Random(0)
    for _ in range(num_tests):
        scale = rng.randint(0, max_scale)
        instance = ExactCover.random_instance(rng, scale)
        sat_instance = reduce(instance)
        # Validate both instances (should not raise)
        ExactCover.validate(instance)
        Sat.validate(sat_instance)
        exact = ExactCover.is_yes(instance)
        sat = Sat.is_yes(sat_instance)
        if exact != sat:
            print("Mismatch!")
            print("ExactCover instance:", instance)
            print("SAT instance:", sat_instance)
            print("ExactCover answer", exact, "SAT answer", sat)
            return False
    return True


def test_edge_cases():
    # u = 0, no sets
    inst = {"universe_size": 0, "sets": []}
    sat = reduce(inst)
    assert ExactCover.is_yes(inst) == Sat.is_yes(sat)
    # u = 0 with some empty sets
    inst = {"universe_size": 0, "sets": [[], []]}
    sat = reduce(inst)
    assert ExactCover.is_yes(inst) == Sat.is_yes(sat)
    # element with no covering set -> unsat
    inst = {"universe_size": 1, "sets": []}
    sat = reduce(inst)
    assert not Sat.is_yes(sat)
    # duplicate non-empty sets should not affect answer
    inst = {"universe_size": 2, "sets": [[0,1], [0,1]]}
    sat = reduce(inst)
    assert ExactCover.is_yes(inst) == Sat.is_yes(sat)
    return True

if __name__ == "__main__":
    ok = test_random_instances()
    ok = ok and test_edge_cases()
    print("All tests passed" if ok else "Tests failed")
