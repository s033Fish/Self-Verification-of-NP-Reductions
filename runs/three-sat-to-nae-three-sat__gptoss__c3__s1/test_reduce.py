import random
import importlib

problems = importlib.import_module('problems')
ThreeSat = problems.ThreeSat
NaeThreeSat = problems.NaeThreeSat
from reduce import reduce

def test_random_instances(trials=200, max_scale=4):
    rng = random.Random(0)
    for _ in range(trials):
        scale = rng.randint(0, max_scale)
        instance = ThreeSat.random_instance(rng, scale)
        # ensure instance is valid
        ThreeSat.validate(instance)
        yes3 = ThreeSat.is_yes(instance)
        red = reduce(instance)
        NaeThreeSat.validate(red)
        yesN = NaeThreeSat.is_yes(red)
        assert yes3 == yesN, f"Mismatch on instance {instance}: 3SAT {yes3} vs NAE {yesN}"
    return True

if __name__ == "__main__":
    passed = test_random_instances()
    print("All tests passed?", passed)
