import itertools
import json
from problems import ThreeSat, SubsetSum, InvalidInstance
from reduce import reduce

def solve_three_sat(instance):
    ThreeSat.validate(instance)
    m = instance['num_vars']
    clauses = instance['clauses']
    for mask in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (mask >> var) & 1
                if lit > 0 and val == 1:
                    clause_ok = True
                    break
                if lit < 0 and val == 0:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def solve_subset_sum(instance):
    SubsetSum.validate(instance)
    numbers = instance['numbers']
    target = instance['target']
    n = len(numbers)
    for r in range(n+1):
        for combo in itertools.combinations(range(n), r):
            if sum(numbers[i] for i in combo) == target:
                return True
    return False

# Generate small random 3-SAT instances for testing
def generate_instances():
    # small m up to 4, generate all possible clauses combos
    for m in range(0,5):
        # generate all possible literals for variables 1..m
        literals = []
        for v in range(1,m+1):
            literals.append(v)
            literals.append(-v)
        # all possible clauses: choose 3 distinct variables
        var_combos = list(itertools.combinations(range(1,m+1), 3)) if m>=3 else []
        clause_options = []
        for combo in var_combos:
            # for each variable, choose sign +/-
            for signs in itertools.product([1,-1], repeat=3):
                clause = [signs[i]*combo[i] for i in range(3)]
                clause_options.append(clause)
        # generate up to 3 clauses (including empty set)
        for num_clauses in range(0,4):
            for clauses in itertools.combinations_with_replacement(clause_options, num_clauses):
                yield {'num_vars': m, 'clauses': [list(c) for c in clauses]}


def main():
    total = 0
    passed = 0
    for inst in generate_instances():
        total += 1
        sat_ans = solve_three_sat(inst)
        red = reduce(inst)
        ss_ans = solve_subset_sum(red)
        if sat_ans == ss_ans:
            passed += 1
        else:
            print('Mismatch', inst, sat_ans, ss_ans, red)
            break
    print('Tests run:', total, 'passed:', passed)
    # write verdict
    verdict = {
        'verified': total == passed,
        'tests_run': total,
        'tests_passed': passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f)

if __name__ == '__main__':
    main()
