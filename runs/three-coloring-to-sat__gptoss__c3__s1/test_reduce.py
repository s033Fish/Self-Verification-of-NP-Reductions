import random
from problems import ThreeColoring, Sat
from reduce import reduce

def test_all_small():
    count = 0
    for instance in ThreeColoring.enumerate_instances(scale=4):
        sat_inst = reduce(instance)
        assert ThreeColoring.is_yes(instance) == Sat.is_yes(sat_inst)
        count += 1
    print('tested', count, 'small instances')

def test_random():
    rng = random.Random(0)
    for n in range(0, 6):
        for _ in range(20):
            inst = ThreeColoring.random_instance(rng, n)
            sat_inst = reduce(inst)
            assert ThreeColoring.is_yes(inst) == Sat.is_yes(sat_inst)
    print('random tests passed')

if __name__ == '__main__':
    test_all_small()
    test_random()
