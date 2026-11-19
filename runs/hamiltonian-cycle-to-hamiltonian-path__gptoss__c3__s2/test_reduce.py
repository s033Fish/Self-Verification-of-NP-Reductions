import sys
from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce

def main():
    max_scale = 4  # up to 4 vertices, manageable enumeration
    total = 0
    passed = 0
    for instance in HamiltonianCycle.enumerate_instances(max_scale):
        total += 1
        src_ans = HamiltonianCycle.is_yes(instance)
        tgt_instance = reduce(instance)
        # Validate target instance (should be a valid HamiltonianPath instance)
        try:
            HamiltonianPath.validate(tgt_instance)
        except Exception as e:
            print('Validation failed for reduced instance:', e, file=sys.stderr)
            continue
        tgt_ans = HamiltonianPath.is_yes(tgt_instance)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print('Mismatch:', instance, src_ans, tgt_instance, tgt_ans, file=sys.stderr)
    print(f'Tests run: {total}, passed: {passed}')
    # Write verdict.json
    import json
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    if total != passed:
        sys.exit(1)

if __name__ == '__main__':
    main()
