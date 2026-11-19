import sys
import random
from problems import ThreeSat, Clique
from reduce import reduce


def main():
    total = 0
    passed = 0
    # Test all instances up to scale 3 (num_vars <=3). This is manageable.
    for instance in ThreeSat.enumerate_instances(scale=3):
        total += 1
        src_yes = ThreeSat.is_yes(instance)
        target = reduce(instance)
        tgt_yes = Clique.is_yes(target)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch!", instance, "src", src_yes, "tgt", tgt_yes, "target", target, file=sys.stderr)
    # Also test some random instances with larger scales.
    rng = random.Random(42)
    for scale in range(0, 6):
        for _ in range(30):
            total += 1
            inst = ThreeSat.random_instance(rng, scale)
            src_yes = ThreeSat.is_yes(inst)
            target = reduce(inst)
            tgt_yes = Clique.is_yes(target)
            if src_yes == tgt_yes:
                passed += 1
            else:
                print("Mismatch! (random)", inst, "src", src_yes, "tgt", tgt_yes, "target", target, file=sys.stderr)
    print(f"Passed {passed}/{total} tests")
    # Write verdict.json
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    import json, pathlib
    pathlib.Path('verdict.json').write_text(json.dumps(verdict))
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
