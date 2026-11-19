import json
import sys
from pathlib import Path

import problems
from sat_solver import sat_satisfiable, threesat_satisfiable
from reduce import reduce as reduce_fn


def generate_instances():
    """Yield a modest collection of SAT instances covering edge cases.

    Exhaustively enumerating all possible formulas quickly explodes; the
    original implementation timed‑out.  Instead we construct a curated set
    that exercises the important behaviours of the reduction:

    * empty formula, empty clause, unit clause, binary clause, ternary
      clause, clause with duplicate literals, tautological clause, and a
      longer clause (k >= 4).
    * various numbers of variables (0‑4).
    """
    def inst(num_vars, clauses):
        return {"num_vars": num_vars, "clauses": clauses}

    # 0 variables
    yield inst(0, [])  # trivially satisfiable
    # 1 variable cases
    yield inst(1, [[]])  # unsatisfiable (empty clause)
    yield inst(1, [[1]])  # satisfiable
    yield inst(1, [[-1]])  # satisfiable
    yield inst(1, [[1, 1, -1]])  # tautology, should be dropped
    # 2 variables cases
    yield inst(2, [[1, -2]])
    yield inst(2, [[1, 2]])
    yield inst(2, [[1, 2, -1]])  # tautology inside longer clause
    # 3 variables cases
    yield inst(3, [[1, 2, 3]])
    # Clause with duplicates
    yield inst(3, [[1, 1, 2]])
    # Multiple clauses
    yield inst(3, [[1, -2], [2, 3]])
    # 4 variables, k=4 clause
    yield inst(4, [[1, 2, 3, 4]])


def main():
    total = 0
    passed = 0
    for instance in generate_instances():
        total += 1
        # Validate source instance
        try:
            problems.Sat.validate(instance)
        except Exception as e:
            print("Source validation failed", e, file=sys.stderr)
            continue
        src_ans = sat_satisfiable(instance)
        try:
            red = reduce_fn(instance)
        except Exception as e:
            print("Reduction raised exception", e, file=sys.stderr)
            continue
        try:
            problems.ThreeSat.validate(red)
        except Exception as e:
            print("Target validation failed", e, file=sys.stderr)
            continue
        tgt_ans = threesat_satisfiable(red)
        if src_ans == tgt_ans:
            passed += 1
        else:
            print("Mismatch!", instance, red, src_ans, tgt_ans, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict, indent=2))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
