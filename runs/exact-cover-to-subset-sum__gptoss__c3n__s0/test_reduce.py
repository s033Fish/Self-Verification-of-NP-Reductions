import itertools
import random
import sys
from problems import ExactCover, SubsetSum
from reduce import reduce

def solve_exact_cover(instance):
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    universe = set(range(u))
    # iterate over all subsets of sets (by index)
    for r in range(n+1):
        for combo in itertools.combinations(range(n), r):
            used = set()
            ok = True
            for idx in combo:
                s = set(sets[idx])
                # check disjointness
                if used & s:
                    ok = False
                    break
                used |= s
            if ok and used == universe:
                return True
    return False

def solve_subset_sum(instance):
    numbers = instance["numbers"]
    target = instance["target"]
    if target < 0:
        return False
    # simple DP for non-negative numbers
    reachable = {0}
    for num in numbers:
        new = set()
        for val in reachable:
            new.add(val + num)
        reachable |= new
    return target in reachable

def random_exact_cover_instance(max_u=4, max_sets=5):
    u = random.randint(0, max_u)
    sets = []
    for _ in range(random.randint(0, max_sets)):
        # generate random subset
        subset = [i for i in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}

def test_one(instance):
    ec = solve_exact_cover(instance)
    red = reduce(instance)
    ss = solve_subset_sum(red)
    if ec != ss:
        print("Mismatch!", instance, "->", red, ec, ss)
        return False
    return True

def main():
    # deterministic small exhaustive tests for u<=3, all possible set families up to size 4
    for u in range(0, 4):
        all_subsets = []
        elems = list(range(u))
        # generate all possible subsets (including empty)
        all_subsets = [list(s) for r in range(u+1) for s in itertools.combinations(elems, r)]
        # generate families of up to 3 sets (allow repetitions)
        for size in range(0, 4):
            for family in itertools.product(all_subsets, repeat=size):
                instance = {"universe_size": u, "sets": list(family)}
                if not test_one(instance):
                    sys.exit(1)
    # random tests
    for _ in range(200):
        inst = random_exact_cover_instance()
        if not test_one(inst):
            sys.exit(1)
    print("All tests passed")

if __name__ == "__main__":
    main()
