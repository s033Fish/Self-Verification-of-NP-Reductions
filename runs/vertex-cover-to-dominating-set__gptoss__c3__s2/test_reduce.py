import random
from problems import VertexCover, DominatingSet
from reduce import reduce

def test_random_instances():
    rng = random.Random(0)
    # test 100 random instances with small scale (up to 4 vertices)
    for _ in range(100):
        scale = 4
        src = VertexCover.random_instance(rng, scale)
        tgt = reduce(src)
        src_ans = VertexCover.is_yes(src)
        tgt_ans = DominatingSet.is_yes(tgt)
        assert src_ans == tgt_ans, f"Mismatch on {src} -> {tgt}"

def test_enumerate_small():
    # enumerate all instances up to scale 3 (should be manageable)
    count = 0
    for src in VertexCover.enumerate_instances(3):
        tgt = reduce(src)
        assert VertexCover.is_yes(src) == DominatingSet.is_yes(tgt)
        count += 1
    # ensure we actually tested some instances
    assert count > 0

if __name__ == "__main__":
    test_random_instances()
    test_enumerate_small()
    print("All tests passed", count if 'count' in locals() else "")
