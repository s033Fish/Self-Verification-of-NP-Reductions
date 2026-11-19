import json, sys, random
from problems import IndependentSet, VertexCover
from reduce import reduce

def run_tests():
    total = 0
    passed = 0
    # Edge case tests
    edge_cases = [
        {"n": 5, "edges": [], "k": 0},  # k <= 0 -> yes
        {"n": 5, "edges": [], "k": -3},  # k <= 0 -> yes
        {"n": 5, "edges": [], "k": 6},   # k > n -> no
        {"n": 3, "edges": [[0,1],[1,2]], "k": 2},  # typical yes/no depends
    ]
    for inst in edge_cases:
        total += 1
        try:
            reduced = reduce(inst)
            ok = IndependentSet.is_yes(inst) == VertexCover.is_yes(reduced)
            if ok:
                passed += 1
            else:
                print("Mismatch on edge case", inst, reduced)
        except Exception as e:
            print("Error on edge case", e)
    # Random tests
    rng = random.Random(0)
    for scale in range(1, 4):  # small scales
        for _ in range(30):
            inst = IndependentSet.random_instance(rng, scale)
            total += 1
            reduced = reduce(inst)
            if IndependentSet.is_yes(inst) == VertexCover.is_yes(reduced):
                passed += 1
            else:
                print("Mismatch on random instance", inst, reduced)
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    run_tests()
