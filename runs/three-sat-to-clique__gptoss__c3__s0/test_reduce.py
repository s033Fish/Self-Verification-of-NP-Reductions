import sys
from problems import ThreeSat, Clique
from reduce import reduce


def main():
    scale = 3
    total = 0
    passed = 0
    for instance in ThreeSat.enumerate_instances(scale):
        total += 1
        # reduce
        try:
            target = reduce(instance)
        except Exception as e:
            print(f"Reduction raised exception on {instance}: {e}")
            continue
        # validate target
        try:
            Clique.validate(target)
        except Exception as e:
            print(f"Target validation failed on {target}: {e}")
            continue
        src_yes = ThreeSat.is_yes(instance)
        tgt_yes = Clique.is_yes(target)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch!", instance, src_yes, target, tgt_yes)
    # write verdict
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    import json, pathlib
    pathlib.Path('verdict.json').write_text(json.dumps(verdict))
    print(json.dumps(verdict))
    return passed == total

if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
