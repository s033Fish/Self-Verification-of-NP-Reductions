import random
from problems import ThreeSat, NaeThreeSat
from reduce import reduce

def test_exhaustive(scale=2):
    # enumerate all instances up to given scale (small)
    count = 0
    for instance in ThreeSat.enumerate_instances(scale):
        # skip invalid? enumerate_instances returns valid only.
        reduced = reduce(instance)
        # both should be valid
        ThreeSat.validate(instance)
        NaeThreeSat.validate(reduced)
        assert ThreeSat.is_yes(instance) == NaeThreeSat.is_yes(reduced), (instance, reduced)
        count += 1
    print('exhaustive tested', count, 'instances')

def test_random(trials=100):
    rng = random.Random(0)
    for _ in range(trials):
        scale = rng.randint(1, 4)
        instance = ThreeSat.random_instance(rng, scale)
        reduced = reduce(instance)
        ThreeSat.validate(instance)
        NaeThreeSat.validate(reduced)
        assert ThreeSat.is_yes(instance) == NaeThreeSat.is_yes(reduced)
    print('random tested', trials, 'instances')

if __name__ == '__main__':
    test_exhaustive(2)
    test_random(200)
