import itertools
import json
import random
import sys
from pathlib import Path

sys.path.append(str(Path('.').resolve()))
from problems import ThreeColoring, ThreeSat
from reduce import reduce


def three_coloring_bruteforce(instance):
    n = instance['n']
    edges = instance['edges']
    for colors in itertools.product(range(3), repeat=n):
        if all(colors[u] != colors[v] for u, v in edges):
            return True
    return False


def three_sat_bruteforce(instance):
    m = instance['num_vars']
    clauses = instance['clauses']
    for assignment in itertools.product([False, True], repeat=m):
        if all(any((lit > 0 and assignment[abs(lit)-1]) or (lit < 0 and not assignment[abs(lit)-1]) for lit in clause) for clause in clauses):
            return True
    return False


def random_graph(max_n=3):
    n = random.randint(0, max_n)
    possible_edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    edges = [list(e) for e in possible_edges if random.choice([True, False])]
    return {"n": n, "edges": edges}


def run_tests(num_trials=30):
    passed = 0
    for _ in range(num_trials):
        inst = random_graph()
        ThreeColoring.validate(inst)
        src = three_coloring_bruteforce(inst)
        red = reduce(inst)
        ThreeSat.validate(red)
        tgt = three_sat_bruteforce(red)
        if src == tgt:
            passed += 1
        else:
            print("Mismatch!", inst, src, tgt)
            break
    return passed, num_trials

if __name__ == '__main__':
    passed, total = run_tests()
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    print(json.dumps(verdict, indent=2))
    Path('verdict.json').write_text(json.dumps(verdict))
