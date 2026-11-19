import itertools
from problems import ThreeSat, SubsetSum
from reduce import reduce

def test_all_small():
    # enumerate all formulas with up to 3 variables
    count = 0
    for instance in ThreeSat.enumerate_instances(scale=3):
        # skip formulas with more than, say, 5 clauses to keep runtime low
        if len(instance["clauses"]) > 5:
            continue
        reduced = reduce(instance)
        assert ThreeSat.is_yes(instance) == SubsetSum.is_yes(reduced)
        count += 1
    assert count > 0

def test_random():
    rng = __import__('random').Random(0)
    for m in range(1, 5):
        for _ in range(20):
            inst = ThreeSat.random_instance(rng, m)
            reduced = reduce(inst)
            assert ThreeSat.is_yes(inst) == SubsetSum.is_yes(reduced)

if __name__ == "__main__":
    test_all_small()
    test_random()
    print("All tests passed")
