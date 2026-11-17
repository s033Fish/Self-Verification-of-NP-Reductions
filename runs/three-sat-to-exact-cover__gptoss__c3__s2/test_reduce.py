import json
import random
from problems import ThreeSat, ExactCover
from reduce import reduce

def test_all_small():
    # Use scale 3 for enumeration (as doc says manageable)
    count = 0
    for instance in ThreeSat.enumerate_instances(scale=3):
        # validate both instances
        ThreeSat.validate(instance)
        reduced = reduce(instance)
        ExactCover.validate(reduced)
        yes_src = ThreeSat.is_yes(instance)
        yes_tgt = ExactCover.is_yes(reduced)
        assert yes_src == yes_tgt, f"Mismatch on {instance} -> {reduced}"
        count += 1
    print("tested", count, "instances")

if __name__ == "__main__":
    test_all_small()
