import itertools
from problems import VertexCover, Sat
from reduce import reduce

def test_all():
    # Test all small instances up to scale 4 (vertices up to 4)
    scale = 4
    total = 0
    passed = 0
    for instance in VertexCover.enumerate_instances(scale):
        total += 1
        reduced = reduce(instance)
        # Validate reduced instance (should not raise)
        Sat.validate(reduced)
        ans_src = VertexCover.is_yes(instance)
        ans_red = Sat.is_yes(reduced)
        if ans_src == ans_red:
            passed += 1
        else:
            print("Mismatch!", instance, reduced, ans_src, ans_red)
    print(f"tested {total} instances, passed {passed}")
    return total, passed

if __name__ == "__main__":
    total, passed = test_all()
    # Write verdict.json
    import json
    verdict = {"verified": total == passed, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print("verdict", verdict)
