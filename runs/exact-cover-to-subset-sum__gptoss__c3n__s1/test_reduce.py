import random
import itertools
import json
from problems import ExactCover, SubsetSum
from reduce import reduce


def exact_cover_bruteforce(instance):
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    m = len(sets)
    # Edge: u=0 always yes
    if u == 0:
        return True
    # Enumerate subsets of indices
    for r in range(1, m + 1):
        for combo in itertools.combinations(range(m), r):
            covered = set()
            ok = True
            for i in combo:
                s = sets[i]
                # check disjointness
                if any(elem in covered for elem in s):
                    ok = False
                    break
                covered.update(s)
            if ok and covered == set(range(u)):
                return True
    return False


def subset_sum_bruteforce(instance):
    SubsetSum.validate(instance)
    numbers = instance["numbers"]
    target = instance["target"]
    # Edge cases handled automatically by enumeration
    n = len(numbers)
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == target:
                return True
    return False


def random_exact_cover_instance(max_u=4, max_sets=5, trials=1000):
    instances = []
    for _ in range(trials):
        u = random.randint(0, max_u)
        m = random.randint(0, max_sets)
        sets = []
        for __ in range(m):
            # each set random subset of universe
            subset = [e for e in range(u) if random.choice([True, False])]
            # ensure distinct elements, already
            sets.append(subset)
        instances.append({"universe_size": u, "sets": sets})
    return instances

def main():
    random.seed(0)
    instances = random_exact_cover_instance()
    total = len(instances)
    passed = 0
    for inst in instances:
        ec = exact_cover_bruteforce(inst)
        reduced = reduce(inst)
        ss = subset_sum_bruteforce(reduced)
        if ec == ss:
            passed += 1
        else:
            print("Mismatch!", inst, reduced, ec, ss)
            break
    # also test some explicit edge cases
    edge_cases = [
        {"universe_size": 0, "sets": []},
        {"universe_size": 0, "sets": [[0]]},  # invalid but validator will reject
        {"universe_size": 3, "sets": []},
        {"universe_size": 3, "sets": [[], [0,1], [2]]},
    ]
    for ec_inst in edge_cases:
        try:
            ExactCover.validate(ec_inst)
        except Exception:
            continue
        ec = exact_cover_bruteforce(ec_inst)
        reduced = reduce(ec_inst)
        ss = subset_sum_bruteforce(reduced)
        if ec != ss:
            print("Edge mismatch!", ec_inst, reduced, ec, ss)
            break
        else:
            passed += 1
        total += 1
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict))
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == "__main__":
    main()
