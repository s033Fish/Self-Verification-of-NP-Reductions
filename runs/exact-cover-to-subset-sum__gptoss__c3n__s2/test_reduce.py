import itertools
import random
import json
from typing import List, Dict, Any

from problems import ExactCover, SubsetSum
from reduce import reduce

def exact_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets: List[List[int]] = instance["sets"]
    m = len(sets)
    # Edge case u=0 always yes
    if u == 0:
        return True
    # iterate over subsets of indices
    for r in range(1, m+1):
        for combo in itertools.combinations(range(m), r):
            covered = set()
            ok = True
            for idx in combo:
                s = sets[idx]
                # check disjointness
                for e in s:
                    if e in covered:
                        ok = False
                        break
                    covered.add(e)
                if not ok:
                    break
            if ok and covered == set(range(u)):
                return True
    return False

def subset_sum_bruteforce(instance: Dict[str, Any]) -> bool:
    SubsetSum.validate(instance)
    numbers: List[int] = instance["numbers"]
    target: int = instance["target"]
    if target == 0:
        return True
    if target < 0:
        return False
    n = len(numbers)
    for r in range(1, n+1):
        for combo in itertools.combinations(range(n), r):
            s = sum(numbers[i] for i in combo)
            if s == target:
                return True
    return False

def random_exact_cover(max_universe=4, max_sets=5) -> Dict[str, Any]:
    u = random.randint(0, max_universe)
    sets = []
    for _ in range(random.randint(0, max_sets)):
        # each set can be any subset of universe
        subset = [e for e in range(u) if random.choice([True, False])]
        sets.append(subset)
    return {"universe_size": u, "sets": sets}

def run_tests(num_trials: int = 200) -> Dict[str, int]:
    passed = 0
    for _ in range(num_trials):
        src = random_exact_cover()
        tgt = reduce(src)
        src_ans = exact_cover_bruteforce(src)
        tgt_ans = subset_sum_bruteforce(tgt)
        if src_ans == tgt_ans:
            passed += 1
        else:
            # print failing case for debugging
            print("FAIL")
            print(json.dumps(src, indent=2))
            print(json.dumps(tgt, indent=2))
            print("src_ans", src_ans, "tgt_ans", tgt_ans)
            break
    return {"tests_run": num_trials, "tests_passed": passed}

if __name__ == "__main__":
    result = run_tests(500)
    result["verified"] = result["tests_run"] == result["tests_passed"]
    with open("verdict.json", "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
