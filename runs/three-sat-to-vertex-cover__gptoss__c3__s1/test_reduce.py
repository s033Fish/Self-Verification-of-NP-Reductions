import random
import sys
from problems import ThreeSat, VertexCover
from reduce import reduce

def test_random_trials(num_trials=200):
    rng = random.Random(0)
    for _ in range(num_trials):
        # random scale up to 4 variables
        scale = rng.randint(0, 4)
        instance = ThreeSat.random_instance(rng, scale)
        # Validate and reduce
        ThreeSat.validate(instance)
        vc_instance = reduce(instance)
        VertexCover.validate(vc_instance)
        # Compare answers
        ans_src = ThreeSat.is_yes(instance)
        ans_tgt = VertexCover.is_yes(vc_instance)
        if ans_src != ans_tgt:
            print("Mismatch!", instance, vc_instance, ans_src, ans_tgt)
            return False
    return True

def test_exhaustive(scale=3):
    for inst in ThreeSat.enumerate_instances(scale):
        vc_inst = reduce(inst)
        # validation
        ThreeSat.validate(inst)
        VertexCover.validate(vc_inst)
        if ThreeSat.is_yes(inst) != VertexCover.is_yes(vc_inst):
            print("Exhaustive mismatch", inst)
            return False
    return True

if __name__ == "__main__":
    ok = True
    ok &= test_random_trials(200)
    ok &= test_exhaustive(3)
    sys.exit(0 if ok else 1)
