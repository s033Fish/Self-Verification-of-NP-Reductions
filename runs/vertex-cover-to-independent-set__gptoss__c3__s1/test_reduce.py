import sys
import traceback
from problems import VertexCover, IndependentSet
from reduce import reduce


def run_tests(max_scale=3):
    total = 0
    passed = 0
    for instance in VertexCover.enumerate_instances(max_scale):
        total += 1
        try:
            reduced = reduce(instance)
            src_yes = VertexCover.is_yes(instance)
            tgt_yes = IndependentSet.is_yes(reduced)
            if src_yes != tgt_yes:
                print("FAIL: mismatch", instance, reduced, src_yes, tgt_yes)
            else:
                passed += 1
        except Exception as e:
            print("ERROR on instance", instance)
            traceback.print_exc()
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    print(f"Tests run: {total}, passed: {passed}")
    sys.exit(0 if total == passed else 1)
