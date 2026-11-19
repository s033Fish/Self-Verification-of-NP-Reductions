import sys
from problems import ThreeColoring, IndependentSet
from reduce import reduce


def main():
    tests_run = 0
    tests_passed = 0
    # Enumerate small instances (scale up to 3 vertices)
    for instance in ThreeColoring.enumerate_instances(scale=3):
        tests_run += 1
        source_yes = ThreeColoring.is_yes(instance)
        reduced = reduce(instance)
        target_yes = IndependentSet.is_yes(reduced)
        if source_yes == target_yes:
            tests_passed += 1
        else:
            print("Mismatch!", instance, "source", source_yes, "target", target_yes, file=sys.stderr)
    # Additional edge cases
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 3, "edges": []},
        {"n": 4, "edges": [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]},  # K4, not 3-colorable
    ]
    for instance in edge_cases:
        tests_run += 1
        source_yes = ThreeColoring.is_yes(instance)
        reduced = reduce(instance)
        target_yes = IndependentSet.is_yes(reduced)
        if source_yes == target_yes:
            tests_passed += 1
        else:
            print("Mismatch edge case!", instance, "source", source_yes, "target", target_yes, file=sys.stderr)
    # Write verdict
    verdict = {"verified": tests_run == tests_passed, "tests_run": tests_run, "tests_passed": tests_passed}
    import json, pathlib
    pathlib.Path("verdict.json").write_text(json.dumps(verdict))
    if not verdict["verified"]:
        sys.exit(1)
    print("All tests passed", verdict)

if __name__ == "__main__":
    main()
