import random
from problems import HamiltonianCycle, HamiltonianPath
from reduce import reduce

def test_random(num_trials=200):
    rng = random.Random(0)
    for _ in range(num_trials):
        # scale determines max n; use small values
        scale = rng.randint(0, 5)
        inst = HamiltonianCycle.random_instance(rng, scale)
        # Reduce
        red = reduce(inst)
        # Compare answers
        ans_src = HamiltonianCycle.is_yes(inst)
        ans_tgt = HamiltonianPath.is_yes(red)
        if ans_src != ans_tgt:
            print("Mismatch!", inst, red, ans_src, ans_tgt)
            return False
    return True

if __name__ == "__main__":
    ok = test_random(500)
    print("All tests passed" if ok else "Some tests failed")
