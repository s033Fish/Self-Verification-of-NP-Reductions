import random
import sys
from problems import ThreeColoring, IndependentSet
from reduce import reduce

def check_instance(inst):
    # Validate source
    ThreeColoring.validate(inst)
    # Reduce
    reduced = reduce(inst)
    # Validate target
    IndependentSet.validate(reduced)
    # Compare answers
    src_yes = ThreeColoring.is_yes(inst)
    tgt_yes = IndependentSet.is_yes(reduced)
    if src_yes != tgt_yes:
        print("Mismatch!", inst, reduced, src_yes, tgt_yes)
        return False
    return True

def main():
    rng = random.Random(0)
    # test edge cases
    edge_cases = [
        {"n": 0, "edges": []},
        {"n": 1, "edges": []},
        {"n": 2, "edges": []},
        {"n": 3, "edges": []},
        {"n": 4, "edges": [[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]]},  # K4
    ]
    for inst in edge_cases:
        if not check_instance(inst):
            sys.exit(1)
    # random small instances
    for scale in range(1,5):
        for _ in range(200):
            inst = ThreeColoring.random_instance(rng, scale)
            if not check_instance(inst):
                sys.exit(1)
    print("All tests passed")

if __name__ == "__main__":
    main()
