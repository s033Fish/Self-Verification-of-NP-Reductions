import sys
from problems import ThreeColoring, OneInThreeSat
from reduce import reduce

def run_tests():
    tests = 0
    passed = 0
    # Test small graphs up to n=4 (scale parameter is max n)
    for instance in ThreeColoring.enumerate_instances(4):
        tests += 1
        src_yes = ThreeColoring.is_yes(instance)
        tgt = reduce(instance)
        tgt_yes = OneInThreeSat.is_yes(tgt)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch!", instance, src_yes, tgt_yes, file=sys.stderr)
    # Additional explicit edge cases
    extra = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": [[0,1]]},
        {"n": 3, "edges": [[0,1],[1,2],[0,2]]},  # triangle (3-colorable)
        {"n": 4, "edges": [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]},  # K4 (not 3-colorable)
    ]
    for instance in extra:
        tests += 1
        src_yes = ThreeColoring.is_yes(instance)
        tgt = reduce(instance)
        tgt_yes = OneInThreeSat.is_yes(tgt)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch extra!", instance, src_yes, tgt_yes, file=sys.stderr)
    print(f"Tests run: {tests}, passed: {passed}")
    return tests, passed

if __name__ == "__main__":
    total, ok = run_tests()
    # Write verdict.json
    import json
    verdict = {
        "verified": total == ok,
        "tests_run": total,
        "tests_passed": ok,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print("Verdict written to verdict.json")
