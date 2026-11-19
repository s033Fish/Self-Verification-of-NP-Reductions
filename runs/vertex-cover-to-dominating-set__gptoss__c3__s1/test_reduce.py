import random
import sys

# import problem classes
from problems import VertexCover, DominatingSet
from reduce import reduce

def run_random_tests(num_trials: int = 200):
    rng = random.Random(0)
    for i in range(num_trials):
        # scale determines size; use small scale for brute force
        scale = 4
        inst = VertexCover.random_instance(rng, scale)
        # ensure instance is valid
        VertexCover.validate(inst)
        yes_vc = VertexCover.is_yes(inst)
        red = reduce(inst)
        DominatingSet.validate(red)
        yes_ds = DominatingSet.is_yes(red)
        if yes_vc != yes_ds:
            print("Mismatch on trial", i)
            print("orig", inst)
            print("red", red)
            print("vc", yes_vc, "ds", yes_ds)
            sys.exit(1)
    print("All random tests passed", num_trials)


def run_edge_cases():
    cases = [
        {"n": 0, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": 0},
        {"n": 3, "edges": [], "k": -1},
        {"n": 2, "edges": [[0,1]], "k": 1},
        {"n": 2, "edges": [[0,1]], "k": 0},
    ]
    for inst in cases:
        VertexCover.validate(inst)
        yes_vc = VertexCover.is_yes(inst)
        red = reduce(inst)
        DominatingSet.validate(red)
        yes_ds = DominatingSet.is_yes(red)
        assert yes_vc == yes_ds, f"edge case mismatch {inst} -> {red}"
    print("Edge case tests passed")

if __name__ == "__main__":
    run_edge_cases()
    run_random_tests()
