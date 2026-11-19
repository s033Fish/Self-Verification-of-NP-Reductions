import json
import sys
import traceback
import random
import problems
from reduce import reduce

def main():
    total = 0
    passed = 0
    # We'll test all instances up to scale 4 (small graphs)
    for instance in problems.SOURCE.enumerate_instances(scale=4):
        total += 1
        try:
            reduced = reduce(instance)
            src_yes = problems.SOURCE.is_yes(instance)
            tgt_yes = problems.TARGET.is_yes(reduced)
            if src_yes == tgt_yes:
                passed += 1
            else:
                print("Mismatch!", instance, reduced, src_yes, tgt_yes, file=sys.stderr)
        except Exception as e:
            print("Error on instance", instance, file=sys.stderr)
            traceback.print_exc()
    # also random tests
    rng = random.Random(0)
    for _ in range(200):
        total += 1
        instance = problems.SOURCE.random_instance(rng, scale=5)
        try:
            reduced = reduce(instance)
            src_yes = problems.SOURCE.is_yes(instance)
            tgt_yes = problems.TARGET.is_yes(reduced)
            if src_yes == tgt_yes:
                passed += 1
            else:
                print("Random mismatch!", instance, reduced, src_yes, tgt_yes, file=sys.stderr)
        except Exception as e:
            print("Error on random instance", instance, file=sys.stderr)
            traceback.print_exc()
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == '__main__':
    main()
