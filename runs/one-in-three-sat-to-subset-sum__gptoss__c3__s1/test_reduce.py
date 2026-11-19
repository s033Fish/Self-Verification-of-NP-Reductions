import json
from problems import OneInThreeSat, SubsetSum
from reduce import reduce

def main():
    tests_run = 0
    tests_passed = 0
    # Enumerate instances with up to 3 variables (scale parameter controls max vars)
    for scale in range(0, 4):
        for instance in OneInThreeSat.enumerate_instances(scale):
            tests_run += 1
            src_yes = OneInThreeSat.is_yes(instance)
            tgt_instance = reduce(instance)
            tgt_yes = SubsetSum.is_yes(tgt_instance)
            if src_yes == tgt_yes:
                tests_passed += 1
            else:
                print("Mismatch!", instance, src_yes, tgt_yes)
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
