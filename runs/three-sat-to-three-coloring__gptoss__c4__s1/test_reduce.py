import itertools
import sys
from typing import List, Dict

from problems import ThreeSat, ThreeColoring
from reduce import reduce


def solve_three_sat(instance: Dict) -> bool:
    m = instance["num_vars"]
    clauses = instance["clauses"]
    # iterate over all assignments
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            clause_ok = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1  # 1 means true
                if lit > 0 and val == 1:
                    clause_ok = True
                if lit < 0 and val == 0:
                    clause_ok = True
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def solve_three_coloring(instance: Dict) -> bool:
    n = instance["n"]
    edges = instance["edges"]
    # colors 0,1,2
    for coloring in itertools.product(range(3), repeat=n):
        good = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                good = False
                break
        if good:
            return True
    return False


def generate_all_sat_instances(max_vars=3, max_clauses=2) -> List[Dict]:
    instances = []
    for m in range(max_vars + 1):
        # generate all possible clauses for this m respecting constraints
        literals = []
        for var in range(1, m + 1):
            literals.append(var)
            literals.append(-var)
        # generate all triples of distinct vars
        var_combos = list(itertools.combinations(range(1, m + 1), 3)) if m >= 3 else []
        possible_clauses = []
        for combo in var_combos:
            # for each variable choose sign +/-
            for signs in itertools.product([1, -1], repeat=3):
                clause = [signs[i] * combo[i] for i in range(3)]
                possible_clauses.append(clause)
        # also allow empty clause list
        clause_lists = [[]]
        # up to max_clauses clauses (allow repetitions)
        for r in range(1, max_clauses + 1):
            for combo in itertools.product(possible_clauses, repeat=r):
                clause_lists.append([list(c) for c in combo])
        for clauses in clause_lists:
            instance = {"num_vars": m, "clauses": clauses}
            # validate
            ThreeSat.validate(instance)
            instances.append(instance)
    return instances


def main():
    instances = generate_all_sat_instances(max_vars=3, max_clauses=2)
    total = len(instances)
    passed = 0
    for idx, sat_inst in enumerate(instances):
        try:
            sat_ans = solve_three_sat(sat_inst)
            graph = reduce(sat_inst)
            col_ans = solve_three_coloring(graph)
            if sat_ans != col_ans:
                print("Mismatch!", sat_inst, "->", graph, sat_ans, col_ans)
                sys.exit(1)
            passed += 1
        except Exception as e:
            print("Error on instance", sat_inst, e)
            sys.exit(1)
    print(f"All {passed}/{total} instances passed.")
    # write verdict
    with open('verdict.json', 'w') as f:
        f.write('{"verified": true, "tests_run": %d, "tests_passed": %d}' % (passed, passed))

if __name__ == "__main__":
    main()
