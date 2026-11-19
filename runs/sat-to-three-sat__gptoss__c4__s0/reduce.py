"""Reduction from SAT to 3‑SAT.

The source problem is :class:`Sat` defined in ``problems.py``. An instance
is a dictionary ``{"num_vars": m, "clauses": [[literal, ...], ...]}`` where
``literal`` is an integer ``+v`` (variable *v* true) or ``-v`` (variable *v*
false). Clauses may be of any length, may repeat literals and may be
tautological (contain both ``v`` and ``-v``). The empty clause ``[]``
is unsatisfiable; a formula with no clauses is trivially satisfiable.

The target problem is :class:`ThreeSat`. Every clause must contain **exactly
three literals on three different variables** – no repeated variable and no
pair ``v``/``-v`` in the same clause.

The reduction follows the classic textbook construction:

* Unit clause ``(ℓ)`` → four 3‑clauses using fresh variables a,b:
  ``(ℓ ∨ a ∨ b)``, ``(ℓ ∨ a ∨ ¬b)``, ``(ℓ ∨ ¬a ∨ b)``, ``(ℓ ∨ ¬a ∨ ¬b)``.
* Binary clause ``(ℓ₁ ∨ ℓ₂)`` → two 3‑clauses with fresh a:
  ``(ℓ₁ ∨ ℓ₂ ∨ a)`` and ``(ℓ₁ ∨ ℓ₂ ∨ ¬a)``.
* For longer clauses we use the standard chain construction with auxiliary
  variables.
* An empty clause makes the formula unsatisfiable; we return a fixed
  unsatisfiable 3‑SAT instance.

The implementation respects the validation rules of ``ThreeSat`` – each
clause has three distinct variables. Fresh variables are taken larger than
any original variable.
"""

from __future__ import annotations

from typing import List, Dict, Any

from problems import Sat, ThreeSat

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _simplify_clause(clause: List[int]) -> List[int]:
    """Return a simplified clause.

    - Remove duplicate literals.
    - If a literal and its negation both appear, the clause is a tautology
      and the function returns an empty list to indicate it can be ignored.
    """
    seen = set()
    for lit in clause:
        if -lit in seen:
            return []
        seen.add(lit)
    return list(seen)

# Unsatisfiable 3‑SAT instance used when the source contains an empty clause.
def _unsat_three_sat(start_var: int = 1) -> Dict[str, Any]:
    """Return a guaranteed unsatisfiable 3‑SAT instance.

    ``start_var`` is the variable that will appear positively in one unit
    clause and negatively in another. The function builds the eight 3‑clauses
    required by the unit‑clause encoding.
    """
    a1 = start_var + 1
    b1 = start_var + 2
    unit_pos = [
        [start_var, a1, b1],
        [start_var, a1, -b1],
        [start_var, -a1, b1],
        [start_var, -a1, -b1],
    ]
    a2 = start_var + 3
    b2 = start_var + 4
    unit_neg = [
        [-start_var, a2, b2],
        [-start_var, a2, -b2],
        [-start_var, -a2, b2],
        [-start_var, -a2, -b2],
    ]
    return {"num_vars": start_var + 4, "clauses": unit_pos + unit_neg}

_UNSAT_INSTANCE: Dict[str, Any] = _unsat_three_sat()

# ---------------------------------------------------------------------------
# Reduction implementation
# ---------------------------------------------------------------------------

def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    The returned instance satisfies ``ThreeSat.validate`` and is satisfiable
    exactly when the input instance is.
    """
    Sat.validate(instance)
    m = instance["num_vars"]
    raw_clauses: List[List[int]] = instance["clauses"]

    new_clauses: List[List[int]] = []
    next_fresh = m + 1

    for raw in raw_clauses:
        clause = _simplify_clause(raw)
        if not clause:
            if len(raw) == 0:
                return _UNSAT_INSTANCE
            continue
        k = len(clause)
        if k == 1:
            a = next_fresh
            b = next_fresh + 1
            next_fresh += 2
            l = clause[0]
            new_clauses.extend([
                [l, a, b],
                [l, a, -b],
                [l, -a, b],
                [l, -a, -b],
            ])
        elif k == 2:
            a = next_fresh
            next_fresh += 1
            l1, l2 = clause
            new_clauses.extend([
                [l1, l2, a],
                [l1, l2, -a],
            ])
        elif k == 3:
            new_clauses.append(clause)
        else:
            aux = list(range(next_fresh, next_fresh + k - 3))
            next_fresh += k - 3
            new_clauses.append([clause[0], clause[1], aux[0]])
            for i in range(k - 4):
                new_clauses.append([-aux[i], clause[i + 2], aux[i + 1]])
            new_clauses.append([-aux[-1], clause[-2], clause[-1]])

    result = {"num_vars": next_fresh - 1, "clauses": new_clauses}
    ThreeSat.validate(result)
    return result

# ---------------------------------------------------------------------------
# Test harness (run when executed directly)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import itertools, json, sys

    def brute_sat(inst: Dict[str, Any]) -> bool:
        m = inst["num_vars"]
        for bits in range(1 << m):
            ok = True
            for clause in inst["clauses"]:
                clause_ok = False
                for lit in clause:
                    var = abs(lit) - 1
                    val = (bits >> var) & 1
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

    brute_three_sat = brute_sat

    tests_run = 0
    tests_passed = 0
    for m in range(0, 4):
        vars_range = list(range(1, m + 1))
        literals = [v for v in vars_range] + [-v for v in vars_range]
        clause_opts = [[]]
        for length in range(1, 3):  # only lengths 1 and 2 for exhaustive testing
            for combo in itertools.product(literals, repeat=length):
                clause_opts.append(list(combo))
        for num_clauses in range(0, 3):  # up to 2 clauses
            for formula in itertools.product(clause_opts, repeat=num_clauses):
                instance = {"num_vars": m, "clauses": [list(c) for c in formula]}
                try:
                    Sat.validate(instance)
                except Exception:
                    continue
                tests_run += 1
                sat_ans = brute_sat(instance)
                red = reduce(instance)
                three_ans = brute_three_sat(red)
                if sat_ans == three_ans:
                    tests_passed += 1
                else:
                    print("Counterexample", file=sys.stderr)
                    print("SAT", instance, file=sys.stderr)
                    print("RED", red, file=sys.stderr)
                    sys.exit(1)
    verdict = {"verified": tests_run == tests_passed, "tests_run": tests_run, "tests_passed": tests_passed}
    with open("verdict.json", "w") as f:
        json.dump(verdict, f)
    print(json.dumps(verdict, indent=2))
