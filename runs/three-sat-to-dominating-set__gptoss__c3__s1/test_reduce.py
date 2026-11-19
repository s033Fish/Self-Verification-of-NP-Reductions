import json
from problems import ThreeSat, DominatingSet
from reduce import reduce


def main():
    total = 0
    passed = 0
    # enumerate small instances; scale 3 is reasonable (as doc says)
    for instance in ThreeSat.enumerate_instances(scale=3):
        total += 1
        # reduce
        graph = reduce(instance)
        # compare answers
        ans_sat = ThreeSat.is_yes(instance)
        ans_dom = DominatingSet.is_yes(graph)
        if ans_sat == ans_dom:
            passed += 1
        else:
            print("Mismatch!", instance, graph, ans_sat, ans_dom)
            break
    print(f"Tests run: {total}, passed: {passed}")
    verified = (total == passed)
    with open('verdict.json', 'w') as f:
        json.dump({"verified": verified, "tests_run": total, "tests_passed": passed}, f)
    if not verified:
        raise SystemExit("Verification failed")

if __name__ == "__main__":
    main()
