import random
from problems import Clique, Sat
from reduce import reduce

def test_all_enumerated(scale=3):
    count = 0
    for inst in Clique.enumerate_instances(scale):
        sat_inst = reduce(inst)
        # Validate both instances (optional)
        Clique.validate(inst)
        Sat.validate(sat_inst)
        assert Clique.is_yes(inst) == Sat.is_yes(sat_inst), f"Mismatch on {inst} -> {sat_inst}"
        count += 1
    print(f"Enumerated {count} instances up to scale {scale} passed.")

def test_random(num=200, max_scale=5):
    rng = random.Random(0)
    for _ in range(num):
        scale = rng.randint(0, max_scale)
        inst = Clique.random_instance(rng, scale)
        sat_inst = reduce(inst)
        Clique.validate(inst)
        Sat.validate(sat_inst)
        assert Clique.is_yes(inst) == Sat.is_yes(sat_inst), f"Random mismatch on {inst}"
    print(f"Random {num} instances up to scale {max_scale} passed.")

if __name__ == "__main__":
    test_all_enumerated(3)
    test_random(200, 5)
