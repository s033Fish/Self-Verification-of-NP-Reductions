import random
import sys
from problems import OneInThreeSat, ThreeSat
from reduce import reduce

def main():
    total = 0
    passed = 0
    # Enumerate all source instances (scale up to exhaustive_scale)
    for instance in OneInThreeSat.enumerate_instances(OneInThreeSat.exhaustive_scale):
        total += 1
        src_ans = OneInThreeSat.is_yes(instance)
        tgt_instance = reduce(instance)
        # Validate target instance (should not raise)
        ThreeSat.validate(tgt_instance)
        tgt_ans = ThreeSat.is_yes(tgt_instance)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", instance, src_ans, tgt_ans, file=sys.stderr)
    # Also test some random instances
    rng = random.Random(0)
    for _ in range(200):
        instance = OneInThreeSat.random_instance(rng, OneInThreeSat.exhaustive_scale)
        total += 1
        src_ans = OneInThreeSat.is_yes(instance)
        tgt_instance = reduce(instance)
        ThreeSat.validate(tgt_instance)
        tgt_ans = ThreeSat.is_yes(tgt_instance)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Random mismatch!", instance, src_ans, tgt_ans, file=sys.stderr)
    print(f"Tests run: {total}, passed: {passed}")
    # Write verdict.json
    verified = (total == passed)
    import json
    with open('verdict.json', 'w') as f:
        json.dump({"verified": verified, "tests_run": total, "tests_passed": passed}, f)

if __name__ == "__main__":
    main()
