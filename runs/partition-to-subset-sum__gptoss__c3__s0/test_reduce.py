import random
from problems import Partition, SubsetSum
from reduce import reduce

def test_random_instances(num_trials=200, max_scale=6):
    rng = random.Random(0)
    for scale in range(max_scale + 1):
        for _ in range(num_trials):
            inst = Partition.random_instance(rng, scale)
            Partition.validate(inst)
            yes_part = Partition.is_yes(inst)
            reduced = reduce(inst)
            SubsetSum.validate(reduced)
            yes_subset = SubsetSum.is_yes(reduced)
            assert yes_part == yes_subset, f"Mismatch on {inst} -> {reduced}"

def test_edge_cases():
    # Empty list
    inst = {"numbers": []}
    assert Partition.is_yes(inst)
    reduced = reduce(inst)
    assert reduced == {"numbers": [], "target": 0}
    assert SubsetSum.is_yes(reduced)
    # Odd total (no partition possible)
    inst = {"numbers": [1, 2]}
    assert not Partition.is_yes(inst)
    reduced = reduce(inst)
    assert reduced["target"] < 0
    assert not SubsetSum.is_yes(reduced)
    # Even total
    inst = {"numbers": [1, 1]}
    assert Partition.is_yes(inst)
    reduced = reduce(inst)
    assert reduced["target"] == 1
    assert SubsetSum.is_yes(reduced)
    # Zeros
    inst = {"numbers": [0, 0, 0]}
    assert Partition.is_yes(inst)
    reduced = reduce(inst)
    assert reduced["target"] == 0
    assert SubsetSum.is_yes(reduced)

if __name__ == "__main__":
    test_random_instances()
    test_edge_cases()
    print("All tests passed.")
