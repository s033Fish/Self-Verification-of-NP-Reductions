import random
import itertools
import json
from typing import List, Dict, Any

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce, _is_nae_satisfiable


def three_coloring_bruteforce(instance: Dict[str, Any]) -> bool:
    ThreeColoring.validate(instance)
    n = instance['n']
    edges = [(u, v) for u, v in instance['edges']]
    for coloring in itertools.product(range(3), repeat=n):
        ok = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                ok = False
                break
        if ok:
            return True
    return False


def generate_random_nae_instance(m: int, clause_count: int) -> Dict[str, Any]:
    # generate random clauses respecting constraints
    clauses = []
    vars_list = list(range(1, m+1))
    for _ in range(clause_count):
        # pick 3 distinct vars
        chosen = random.sample(vars_list, 3)
        clause = []
        for var in chosen:
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {'num_vars': m, 'clauses': clauses}


def run_tests(num_trials: int = 200) -> None:
    passed = 0
    for _ in range(num_trials):
        m = random.randint(0, 4)  # allow 0 vars
        # ensure if m<3 and we have clauses, we skip (invalid per spec)
        clause_count = random.randint(0, 4)
        if m < 3 and clause_count > 0:
            # make sure to produce valid instance: if m<3, we must have 0 clauses
            clause_count = 0
        instance = generate_random_nae_instance(m, clause_count)
        # validate
        NaeThreeSat.validate(instance)
        # compute answers
        sat = _is_nae_satisfiable(instance)
        reduced = reduce(instance)
        ThreeColoring.validate(reduced)
        colorable = three_coloring_bruteforce(reduced)
        if sat == colorable:
            passed += 1
        else:
            print('FAIL')
            print('Instance:', json.dumps(instance))
            print('Reduced:', json.dumps(reduced))
            print('sat', sat, 'colorable', colorable)
            break
    print(f'Passed {passed}/{num_trials}')
    # write verdict
    verdict = {
        'verified': passed == num_trials,
        'tests_run': num_trials,
        'tests_passed': passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    run_tests(200)
