import random
import itertools
import json
from typing import List, Dict, Any

from reduce import reduce
from problems import ExactCover, Sat, InvalidInstance


def exact_cover_bruteforce(instance: Dict[str, Any]) -> bool:
    ExactCover.validate(instance)
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    # Edge case u==0
    if u == 0:
        return True
    # enumerate all subsets of sets (by bitmask)
    for mask in range(1 << n):
        covered = [0] * u
        ok = True
        for i in range(n):
            if mask >> i & 1:
                for e in sets[i]:
                    if covered[e]:
                        ok = False
                        break
                    covered[e] = 1
                if not ok:
                    break
        if ok and all(covered):
            return True
    return False


def sat_bruteforce(instance: Dict[str, Any]) -> bool:
    Sat.validate(instance)
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # Empty clause => unsat
    for cl in clauses:
        if len(cl) == 0:
            return False
    # iterate assignments
    for bits in range(1 << m):
        assign = [(bits >> i) & 1 == 1 for i in range(m)]  # True/False for var i+1
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit) - 1
                val = assign[var]
                if lit > 0 and val:
                    clause_sat = True
                    break
                if lit < 0 and not val:
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def random_exact_cover(u_max=4, n_max=5, trials=200):
    for _ in range(trials):
        u = random.randint(0, u_max)
        n = random.randint(0, n_max)
        sets = []
        for _ in range(n):
            # each set random subset of universe
            subset = [e for e in range(u) if random.random() < 0.5]
            sets.append(subset)
        instance = {"universe_size": u, "sets": sets}
        yield instance

def main():
    total = 0
    passed = 0
    for inst in random_exact_cover():
        total += 1
        try:
            src_ans = exact_cover_bruteforce(inst)
            red = reduce(inst)
            tgt_ans = sat_bruteforce(red)
            if src_ans == tgt_ans:
                passed += 1
            else:
                print("Mismatch!", inst, red, src_ans, tgt_ans)
        except InvalidInstance as e:
            print("Invalid instance generated", e)
            continue
    # also test edge case where element uncovered -> unsat clause []
    # Already covered by random generation.
    verdict = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)
    print(json.dumps(verdict))

if __name__ == '__main__':
    main()
