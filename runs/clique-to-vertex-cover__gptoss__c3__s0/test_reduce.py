import random
import sys
from problems import Clique, VertexCover
from reduce import reduce


def run_tests(num_random=200):
    rng = random.Random(0)
    passed = 0
    total = 0
    # Edge case tests
    edge_cases = [
        {"n": 0, "edges": [], "k": -5},
        {"n": 1, "edges": [], "k": 0},
        {"n": 1, "edges": [], "k": 1},
        {"n": 1, "edges": [], "k": 2},
        {"n": 3, "edges": [[0,1],[1,2],[0,2]], "k": 3},
        {"n": 3, "edges": [[0,1],[1,2],[0,2]], "k": 4},
        {"n": 4, "edges": [], "k": 2},
    ]
    for inst in edge_cases:
        total += 1
        try:
            Clique.validate(inst)
            vc_inst = reduce(inst)
            yes_clique = Clique.is_yes(inst)
            yes_vc = VertexCover.is_yes(vc_inst)
            if yes_clique == yes_vc:
                passed += 1
            else:
                print("Mismatch on edge case", inst, yes_clique, yes_vc, file=sys.stderr)
        except Exception as e:
            print("Error on edge case", inst, e, file=sys.stderr)
    # Random tests
    for _ in range(num_random):
        total += 1
        inst = Clique.random_instance(rng, scale=3)
        # ensure validation passes
        Clique.validate(inst)
        vc_inst = reduce(inst)
        VertexCover.validate(vc_inst)
        yes_clique = Clique.is_yes(inst)
        yes_vc = VertexCover.is_yes(vc_inst)
        if yes_clique != yes_vc:
            print("Mismatch!", inst, yes_clique, yes_vc, file=sys.stderr)
        else:
            passed += 1
    return passed, total

if __name__ == "__main__":
    passed, total = run_tests()
    print(f"Passed {passed}/{total} tests")
    sys.exit(0 if passed == total else 1)
