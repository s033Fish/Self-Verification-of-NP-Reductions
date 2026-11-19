import problems
from reduce import reduce

def main():
    total = 0
    passed = 0
    # Use a small scale to keep runtime low
    for instance in problems.Clique.enumerate_instances(scale=3):
        total += 1
        sat_instance = reduce(instance)
        # Validate target instance
        problems.Sat.validate(sat_instance)
        # Compare answers
        clique_ans = problems.Clique.is_yes(instance)
        sat_ans = problems.Sat.is_yes(sat_instance)
        if clique_ans == sat_ans:
            passed += 1
        else:
            print("Mismatch!", instance, sat_instance, clique_ans, sat_ans)
            break
    # Write verdict
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    import json, sys
    json.dump(verdict, open('verdict.json', 'w'))
    print("Verdict:", verdict)
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
