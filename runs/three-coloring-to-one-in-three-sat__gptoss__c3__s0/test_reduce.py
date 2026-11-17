import json
from problems import ThreeColoring, OneInThreeSat
from reduce import reduce

def main():
    tests_run = 0
    tests_passed = 0
    # Use exhaustive scale of source (5) but limit to small n for speed.
    for instance in ThreeColoring.enumerate_instances(4):  # up to 4 vertices
        tests_run += 1
        src_answer = ThreeColoring.is_yes(instance)
        red = reduce(instance)
        tgt_answer = OneInThreeSat.is_yes(red)
        if src_answer == tgt_answer:
            tests_passed += 1
        else:
            print("Mismatch!", instance, src_answer, red, tgt_answer)
    # also random small instances
    import random
    rng = random.Random(0)
    for _ in range(50):
        instance = ThreeColoring.random_instance(rng, 4)
        tests_run += 1
        src_answer = ThreeColoring.is_yes(instance)
        red = reduce(instance)
        tgt_answer = OneInThreeSat.is_yes(red)
        if src_answer == tgt_answer:
            tests_passed += 1
        else:
            print("Mismatch random!", instance, src_answer, red, tgt_answer)
    verdict = {"verified": tests_run == tests_passed, "tests_run": tests_run, "tests_passed": tests_passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
