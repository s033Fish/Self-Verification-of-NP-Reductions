import itertools
from problems import VertexCover, Sat
from reduce import reduce

def test_all():
    # test for small scale
    scale = 3
    count = 0
    for instance in VertexCover.enumerate_instances(scale):
        # skip overly large k combos? enumeration already limited
        reduced = reduce(instance)
        # validate target
        Sat.validate(reduced)
        yes_src = VertexCover.is_yes(instance)
        yes_tgt = Sat.is_yes(reduced)
        assert yes_src == yes_tgt, f"Mismatch on {instance} -> {reduced}"
        count += 1
    print("tested", count, "instances")

if __name__ == "__main__":
    test_all()
