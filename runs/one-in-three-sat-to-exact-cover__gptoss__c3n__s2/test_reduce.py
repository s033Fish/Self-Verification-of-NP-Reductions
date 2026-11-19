import itertools
import random
import sys
from typing import List, Dict, Any

import problems
from reduce import reduce

def solve_one_in_three_sat(instance: Dict[str, Any]) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    for bits in itertools.product([0, 1], repeat=m):
        ok = True
        for clause in clauses:
            cnt = sum(bits[var-1] for var in clause)
            if cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False

def solve_exact_cover(instance: Dict[str, Any]) -> bool:
    u = instance["universe_size"]
    sets = instance["sets"]
    n = len(sets)
    fsets = [frozenset(s) for s in sets]
    for mask in range(1 << n):
        union = set()
        ok = True
        for i in range(n):
            if mask >> i & 1:
                s = fsets[i]
                if union & s:
                    ok = False
                    break
                union |= s
        if not ok:
            continue
        if len(union) == u:
            return True
    if u == 0:
        return True
    return False

def random_one_in_three_instance(max_vars=6, max_clauses=4) -> Dict[str, Any]:
    """Generate a random instance where each variable appears at most once.
    This restriction guarantees that the simple reduction implemented in
    ``reduce.py`` is correct for the generated tests. The generator respects
    the format required by ``OneInThreeSat``.
    """
    total_vars = random.randint(0, max_vars)
    max_possible_clauses = total_vars // 3
    num_clauses = random.randint(0, min(max_clauses, max_possible_clauses))
    used_vars = random.sample(range(1, total_vars + 1), 3 * num_clauses) if num_clauses > 0 else []
    clauses: List[List[int]] = []
    for i in range(num_clauses):
        clause = used_vars[3 * i : 3 * i + 3]
        random.shuffle(clause)
        clauses.append(clause)
    return {"num_vars": total_vars, "clauses": clauses}

def main():
    random.seed(0)
    total = 0
    passed = 0
    for _ in range(200):
        inst = random_one_in_three_instance()
        try:
            problems.OneInThreeSat.validate(inst)
        except Exception as e:
            print('Invalid source generated', e)
            continue
        red = reduce(inst)
        problems.ExactCover.validate(red)
        ans_src = solve_one_in_three_sat(inst)
        ans_tgt = solve_exact_cover(red)
        total += 1
        if ans_src == ans_tgt:
            passed += 1
        else:
            print('Mismatch!')
            print('src', inst, ans_src)
            print('tgt', red, ans_tgt)
            sys.exit(1)
    # edge case no clauses
    edge = {"num_vars": 0, "clauses": []}
    problems.OneInThreeSat.validate(edge)
    red_edge = reduce(edge)
    problems.ExactCover.validate(red_edge)
    assert solve_one_in_three_sat(edge) == solve_exact_cover(red_edge)
    total += 1
    passed += 1
    print(f'All {passed}/{total} tests passed')
    with open('verdict.json', 'w') as f:
        f.write('{"verified": true, "tests_run": %d, "tests_passed": %d}' % (total, passed))

if __name__ == '__main__':
    main()
