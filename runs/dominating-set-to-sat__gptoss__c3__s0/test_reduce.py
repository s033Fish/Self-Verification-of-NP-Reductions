import sys
from problems import DominatingSet, Sat
from reduce import reduce

def main():
    max_scale = 3
    total = 0
    passed = 0
    for instance in DominatingSet.enumerate_instances(max_scale):
        total += 1
        DominatingSet.validate(instance)
        src_yes = DominatingSet.is_yes(instance)
        sat_instance = reduce(instance)
        Sat.validate(sat_instance)
        tgt_yes = Sat.is_yes(sat_instance)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch!", instance, "src", src_yes, "tgt", tgt_yes, file=sys.stderr)
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    print(result)
    import json, pathlib
    pathlib.Path('verdict.json').write_text(json.dumps(result))

if __name__ == "__main__":
    main()
