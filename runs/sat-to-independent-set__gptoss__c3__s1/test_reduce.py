import random
from problems import Sat, IndependentSet
from reduce import reduce

def test_random_small(num_trials=200):
    rng = random.Random(0)
    for _ in range(num_trials):
        scale = rng.randint(0, 4)
        instance = Sat.random_instance(rng, scale)
        sat_yes = Sat.is_yes(instance)
        ind = reduce(instance)
        IndependentSet.validate(ind)
        ind_yes = IndependentSet.is_yes(ind)
        assert sat_yes == ind_yes, f"Mismatch on {instance} -> {ind}"

def test_enumerate_small(scale=2):
    # Enumerate all SAT instances up to a tiny scale. Using scale=2 keeps the
    # total number of instances manageable.
    for instance in Sat.enumerate_instances(scale):
        sat_yes = Sat.is_yes(instance)
        ind = reduce(instance)
        IndependentSet.validate(ind)
        ind_yes = IndependentSet.is_yes(ind)
        assert sat_yes == ind_yes, f"Mismatch on {instance} -> {ind}"

def test_edge_cases():
    # No clauses
    inst = {"num_vars": 5, "clauses": []}
    assert Sat.is_yes(inst)
    ind = reduce(inst)
    IndependentSet.validate(ind)
    assert IndependentSet.is_yes(ind)

    # Empty clause present (unsat)
    inst2 = {"num_vars": 3, "clauses": [[1, -2], []]}
    assert not Sat.is_yes(inst2)
    ind2 = reduce(inst2)
    IndependentSet.validate(ind2)
    assert not IndependentSet.is_yes(ind2)

if __name__ == "__main__":
    test_random_small()
    test_enumerate_small(2)
    test_edge_cases()
    print("All tests passed")
