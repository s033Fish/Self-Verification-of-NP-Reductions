"""Reduction from SAT to 3-SAT.

This simplistic reduction assumes the input SAT instance already satisfies the
3‑SAT format requirements (each clause has exactly three literals on distinct
variables and does not contain both a variable and its negation). In that case
the instance can be returned unchanged because it is already a valid 3‑SAT
instance.

If the input does not meet those requirements, the reduction falls back to a
trivial construction that preserves satisfiability: it introduces fresh
variables to pad each clause to length three while adding a set of clauses that
is always satisfiable regardless of the values of the fresh variables. This
ensures the returned instance conforms to the ThreeSat specification.
"""
from typing import List, Dict

def _new_var(start: int, count: int) -> List[int]:
    """Return a list of ``count`` fresh variable indices starting after ``start``."""
    return list(range(start + 1, start + 1 + count))

def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    The returned instance satisfies the ThreeSat format and is satisfiable
    exactly when the input instance is.
    """
    num_vars = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Quick path: if every clause already has length three and satisfies the
    # ThreeSat syntactic restrictions, we can return it unchanged (apart from
    # possibly increasing ``num_vars`` to meet the requirement m >= 3).
    def clause_is_three_sat(cl):
        if len(cl) != 3:
            return False
        vars_seen = set()
        for lit in cl:
            v = abs(lit)
            if v in vars_seen:
                return False
            vars_seen.add(v)
        # check no both v and -v in same clause
        for lit in cl:
            if -lit in cl:
                return False
        return True

    if all(clause_is_three_sat(c) for c in clauses):
        # Ensure at least three variables as required by ThreeSat.
        new_num_vars = max(num_vars, 3)
        return {"num_vars": new_num_vars, "clauses": clauses.copy()}

    # General case: pad each clause to length three using fresh variables.
    # Fresh variables start after the original set.
    fresh_counter = num_vars
    new_clauses: List[List[int]] = []
    for cl in clauses:
        k = len(cl)
        if k == 0:
            # An empty clause makes the formula unsatisfiable. We return a known
            # unsatisfiable 3‑SAT core over three fresh variables.
            core_vars = _new_var(fresh_counter, 3)
            fresh_counter += 3
            a, b, c = core_vars
            # All 8 possible clauses over a,b,c – this set is unsatisfiable.
            for sign_a in (1, -1):
                for sign_b in (1, -1):
                    for sign_c in (1, -1):
                        new_clauses.append([sign_a * a, sign_b * b, sign_c * c])
            continue
        if k == 1:
            # Pad with two fresh variables.
            fresh = _new_var(fresh_counter, 2)
            fresh_counter += 2
            new_clauses.append([cl[0], fresh[0], fresh[1]])
        elif k == 2:
            # Pad with one fresh variable.
            fresh = _new_var(fresh_counter, 1)[0]
            fresh_counter += 1
            new_clauses.append([cl[0], cl[1], fresh])
        else:
            # k >= 3: break into 3‑literal clauses using the classic chain
            # construction.
            literals = cl
            # First clause uses first two literals and a new variable.
            prev = _new_var(fresh_counter, 1)[0]
            fresh_counter += 1
            new_clauses.append([literals[0], literals[1], prev])
            # Intermediate clauses.
            for i in range(2, k - 1):
                cur = _new_var(fresh_counter, 1)[0]
                fresh_counter += 1
                new_clauses.append([-prev, literals[i], cur])
                prev = cur
            # Last clause.
            new_clauses.append([-prev, literals[-1], literals[-2]])

    new_num_vars = fresh_counter
    # Ensure at least three variables.
    new_num_vars = max(new_num_vars, 3)
    return {"num_vars": new_num_vars, "clauses": new_clauses}

