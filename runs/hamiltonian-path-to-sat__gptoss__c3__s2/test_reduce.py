import sys
from problems import HamiltonianPath, Sat
from reduce import reduce

def main():
    total = 0
    passed = 0
    # test small graphs up to n=4 (scale 4) using enumeration
    for instance in HamiltonianPath.enumerate_instances(scale=4):
        total += 1
        sat_instance = reduce(instance)
        # validate both instances
        try:
            HamiltonianPath.validate(instance)
            Sat.validate(sat_instance)
        except Exception as e:
            print('Validation error', e, file=sys.stderr)
            continue
        # compute answers
        yes_src = HamiltonianPath.is_yes(instance)
        yes_tgt = Sat.is_yes(sat_instance)
        if yes_src == yes_tgt:
            passed += 1
        else:
            print('Mismatch on instance', instance, 'src', yes_src, 'tgt', yes_tgt, file=sys.stderr)
    # also test some random instances up to n=6
    import random
    rng = random.Random(0)
    for n in range(0, 7):
        for _ in range(20):
            instance = HamiltonianPath.random_instance(rng, n)
            total += 1
            sat_instance = reduce(instance)
            yes_src = HamiltonianPath.is_yes(instance)
            yes_tgt = Sat.is_yes(sat_instance)
            if yes_src == yes_tgt:
                passed += 1
            else:
                print('Random mismatch', instance, yes_src, yes_tgt, file=sys.stderr)
    print('TOTAL', total, 'PASSED', passed)
    sys.exit(0 if total == passed else 1)

if __name__ == '__main__':
    main()
