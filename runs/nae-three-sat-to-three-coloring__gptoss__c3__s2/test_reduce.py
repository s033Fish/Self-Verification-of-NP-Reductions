import sys
import traceback

import problems
from reduce import reduce


def main():
    total = 0
    passed = 0
    # enumerate instances up to 3 variables (scale)
    for instance in problems.NaeThreeSat.enumerate_instances(3):
        total += 1
        try:
            src_yes = problems.NaeThreeSat.is_yes(instance)
            tgt = reduce(instance)
            tgt_yes = problems.ThreeColoring.is_yes(tgt)
            if src_yes == tgt_yes:
                passed += 1
            else:
                print("Mismatch!", instance, src_yes, tgt_yes, file=sys.stderr)
        except Exception as e:
            print("Error on instance", instance, file=sys.stderr)
            traceback.print_exc()
    # also test a few random instances
    rng = problems.random.Random(0)
    for _ in range(20):
        instance = problems.NaeThreeSat.random_instance(rng, 4)
        total += 1
        src_yes = problems.NaeThreeSat.is_yes(instance)
        tgt = reduce(instance)
        tgt_yes = problems.ThreeColoring.is_yes(tgt)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Random mismatch!", instance, src_yes, tgt_yes, file=sys.stderr)
    print(f"{passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
