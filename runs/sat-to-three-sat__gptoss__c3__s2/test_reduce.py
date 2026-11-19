import sys
from problems import Sat, ThreeSat
from reduce import reduce

def main():
    tests = 0
    passed = 0
    # Enumerate all small SAT instances with num_vars <= 2
    for instance in Sat.enumerate_instances(scale=2):
        tests += 1
        try:
            reduced = reduce(instance)
        except Exception as e:
            print('Reduction raised on instance', instance, 'error', e)
            continue
        # Check that both answers match
        sat_ans = Sat.is_yes(instance)
        three_ans = ThreeSat.is_yes(reduced)
        if sat_ans == three_ans:
            passed += 1
        else:
            print('Mismatch!')
            print('Original', instance, 'sat_ans', sat_ans)
            print('Reduced', reduced, 'three_ans', three_ans)
    # Also test some random instances up to 3 variables
    import random
    rng = random.Random(0)
    for scale in range(0, 4):
        for _ in range(30):
            instance = Sat.random_instance(rng, scale)
            tests += 1
            reduced = reduce(instance)
            if Sat.is_yes(instance) == ThreeSat.is_yes(reduced):
                passed += 1
            else:
                print('Random mismatch')
                print('Inst', instance)
                print('Red', reduced)
    print('Tests run:', tests, 'Passed:', passed)
    # Write verdict.json
    import json
    verdict = {
        "verified": passed == tests,
        "tests_run": tests,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    if passed != tests:
        sys.exit(1)

if __name__ == '__main__':
    main()
