import json
import random
import sys

from problems import NaeThreeSat, ThreeColoring
from reduce import reduce as reduce_instance
from solve_bruteforce import nae_three_sat_bruteforce, three_coloring_bruteforce


def generate_random_instance(max_vars=4, max_clauses=5):
    m = random.randint(0, max_vars)
    possible_vars = list(range(1, m + 1))
    clauses = []
    num_clauses = random.randint(0, max_clauses)
    for _ in range(num_clauses):
        if len(possible_vars) < 3:
            break
        vars_choice = random.sample(possible_vars, 3)
        clause = []
        for v in vars_choice:
            lit = v if random.choice([True, False]) else -v
            clause.append(lit)
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


def main():
    total = 0
    passed = 0
    mismatches = []
    random.seed(0)
    # keep instances tiny to avoid combinatorial explosion in 3‑coloring brute force
    for _ in range(50):
        inst = generate_random_instance(max_vars=3, max_clauses=1)
        try:
            NaeThreeSat.validate(inst)
        except Exception:
            continue
        sat = nae_three_sat_bruteforce(inst)
        graph = reduce_instance(inst)
        ThreeColoring.validate(graph)
        col = three_coloring_bruteforce(graph)
        total += 1
        if sat == col:
            passed += 1
        else:
            mismatches.append({"instance": inst, "graph": graph, "sat": sat, "col": col})
    # explicit edge cases
    edge_cases = [
        {"num_vars": 0, "clauses": []},
        {"num_vars": 3, "clauses": []},
        {"num_vars": 3, "clauses": [[1, 2, 3]]},
    ]
    for inst in edge_cases:
        NaeThreeSat.validate(inst)
        sat = nae_three_sat_bruteforce(inst)
        graph = reduce_instance(inst)
        ThreeColoring.validate(graph)
        col = three_coloring_bruteforce(graph)
        total += 1
        if sat == col:
            passed += 1
        else:
            mismatches.append({"instance": inst, "graph": graph, "sat": sat, "col": col})
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f, indent=2)
    if mismatches:
        print('Mismatches found:', file=sys.stderr)
        for m in mismatches:
            print(json.dumps(m, indent=2), file=sys.stderr)
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()
