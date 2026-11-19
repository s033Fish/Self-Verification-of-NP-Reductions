import random
from problems import SOURCE, TARGET
from reduce import reduce

def test_all_small():
    # test all graphs up to n=4 (scale parameter is max n)
    scale = 4
    count = 0
    for instance in SOURCE.enumerate_instances(scale):
        # compute answers
        src_yes = SOURCE.is_yes(instance)
        sat_instance = reduce(instance)
        # validate reduction output
        TARGET.validate(sat_instance)
        tgt_yes = TARGET.is_yes(sat_instance)
        assert src_yes == tgt_yes, f"Mismatch on {instance}\nSAT:{sat_instance}\n"
        count += 1
    print("tested", count, "instances")

if __name__ == "__main__":
    test_all_small()
