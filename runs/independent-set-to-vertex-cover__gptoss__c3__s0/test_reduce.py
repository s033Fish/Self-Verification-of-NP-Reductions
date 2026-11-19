import json
from problems import SOURCE, TARGET
from reduce import reduce

def main():
    tests_run = 0
    tests_passed = 0
    # Use a modest scale to keep enumeration fast
    for scale in range(0, 4):  # includes empty graph up to 3 vertices
        for src_instance in SOURCE.enumerate_instances(scale):
            tests_run += 1
            src_answer = SOURCE.is_yes(src_instance)
            tgt_instance = reduce(src_instance)
            # Validate target instance (will raise if invalid)
            TARGET.validate(tgt_instance)
            tgt_answer = TARGET.is_yes(tgt_instance)
            if src_answer == tgt_answer:
                tests_passed += 1
            else:
                print("Mismatch!", src_instance, src_answer, tgt_instance, tgt_answer)
    verdict = {
        "verified": tests_run == tests_passed,
        "tests_run": tests_run,
        "tests_passed": tests_passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
