import random
import itertools
import sys
from problems import Sat, ThreeSat
from reduce import reduce

def sat_bruteforce(instance):
    Sat.validate(instance)
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            # empty clause unsat
            if len(clause) == 0:
                ok = False
                break
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def threesat_bruteforce(instance):
    ThreeSat.validate(instance)
    m = instance['num_vars']
    clauses = instance['clauses']
    for bits in itertools.product([False, True], repeat=m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = bits[var]
                if lit > 0 and val:
                    clause_ok = True
                    break
                if lit < 0 and not val:
                    clause_ok = True
                    break
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False

def random_sat_instance(max_vars=4, max_clauses=5):
    """Generate a random SAT instance that respects the validation rules.
    The original version could produce literals referencing variables that do
    not exist when ``num_vars`` was 0.  This version ensures that literals are
    only created when ``m`` >= 1.  If ``m`` is 0 we simply generate a formula
    with no clauses (which is trivially satisfiable) or only empty clauses.
    """
    m = random.randint(0, max_vars)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        k = random.randint(0, 4)  # allow empty and up to 4 literals
        clause = []
        for __ in range(k):
            if m == 0:
                continue
            var = random.randint(1, m)
            lit = var if random.choice([True, False]) else -var
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}

def run_tests(num_trials=200):
    for i in range(num_trials):
        inst = random_sat_instance()
        sat_ans = sat_bruteforce(inst)
        red = reduce(inst)
        three_ans = threesat_bruteforce(red)
        if sat_ans != three_ans:
            print('Mismatch on instance', inst)
            print('Reduced to', red)
            print('sat', sat_ans, 'three', three_ans)
            sys.exit(1)
    # also test explicit empty clause case
    inst = {"num_vars": 2, "clauses": [[]]}
    sat_ans = sat_bruteforce(inst)
    red = reduce(inst)
    three_ans = threesat_bruteforce(red)
    assert sat_ans == False and three_ans == False
    print('All tests passed')

if __name__ == '__main__':
    run_tests()
