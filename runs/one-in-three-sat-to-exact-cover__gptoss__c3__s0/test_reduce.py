import random
import sys

# Ensure current directory in path
sys.path.append('.')
from problems import OneInThreeSat, ExactCover
from reduce import reduce

def test_random_instances(num_trials=200, scale=4):
    rng = random.Random(0)
    for i in range(num_trials):
        instance = OneInThreeSat.random_instance(rng, scale)
        src_yes = OneInThreeSat.is_yes(instance)
        tgt_instance = reduce(instance)
        # Validate target instance
        ExactCover.validate(tgt_instance)
        tgt_yes = ExactCover.is_yes(tgt_instance)
        if src_yes != tgt_yes:
            print("Mismatch on instance:", instance)
            print("src_yes", src_yes, "tgt_yes", tgt_yes)
            return False
    return True

def test_edge_cases():
    # Empty formula
    empty = {"num_vars": 0, "clauses": []}
    assert OneInThreeSat.is_yes(empty)  # should be yes
    tgt = reduce(empty)
    ExactCover.validate(tgt)
    assert ExactCover.is_yes(tgt)
    # Formula with one clause, 3 vars
    instance = {"num_vars": 3, "clauses": [[1,2,3]]}
    src = OneInThreeSat.is_yes(instance)
    tgt = reduce(instance)
    ExactCover.validate(tgt)
    assert ExactCover.is_yes(tgt) == src

if __name__ == "__main__":
    ok = test_random_instances() and test_edge_cases()
    print("All tests passed" if ok else "Tests failed")
    sys.exit(0 if ok else 1)
