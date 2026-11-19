import itertools
from problems import VertexCover, IndependentSet
from reduce import reduce

def test_all_enumerated():
    # Use a modest scale to keep enumeration feasible.
    scale = 4
    count = 0
    for instance in VertexCover.enumerate_instances(scale):
        reduced = reduce(instance)
        ans_src = VertexCover.is_yes(instance)
        ans_tgt = IndependentSet.is_yes(reduced)
        assert ans_src == ans_tgt, f"Mismatch on {instance} -> {reduced}"
        count += 1
    print(f"Enumerated tests run: {count}")
    return count

def test_random():
    rng = __import__('random').Random(0)
    total = 0
    for scale in range(1, 6):
        for _ in range(10):
            inst = VertexCover.random_instance(rng, scale)
            reduced = reduce(inst)
            assert VertexCover.is_yes(inst) == IndependentSet.is_yes(reduced)
            total += 1
    print(f"Random tests run: {total}")
    return total

if __name__ == "__main__":
    enum = test_all_enumerated()
    rand = test_random()
    total = enum + rand
    # Write verdict
    import json
    verdict = {"verified": True, "tests_run": total, "tests_passed": total}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print("All tests passed, verdict written.")
