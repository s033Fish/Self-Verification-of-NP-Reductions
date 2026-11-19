import random
import sys
from problems import ExactCover, Sat
from reduce import reduce

def main():
    rng = random.Random(0)
    total = 0
    passed = 0
    # Enumerate all ExactCover instances with universe size up to 3
    for scale in range(0, 4):
        for instance in ExactCover.enumerate_instances(scale):
            total += 1
            src_yes = ExactCover.is_yes(instance)
            sat_instance = reduce(instance)
            tgt_yes = Sat.is_yes(sat_instance)
            if src_yes == tgt_yes:
                passed += 1
            else:
                print("Mismatch!", instance, sat_instance, src_yes, tgt_yes, file=sys.stderr)
    # Also test some random larger instances
    for _ in range(200):
        scale = rng.randint(0, 5)
        instance = ExactCover.random_instance(rng, scale)
        total += 1
        src_yes = ExactCover.is_yes(instance)
        sat_instance = reduce(instance)
        tgt_yes = Sat.is_yes(sat_instance)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Random mismatch!", instance, src_yes, tgt_yes, file=sys.stderr)
    print(f"{passed}/{total} tests passed")
    # Write verdict.json
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    import json, pathlib
    pathlib.Path("verdict.json").write_text(json.dumps(verdict))

if __name__ == "__main__":
    main()
