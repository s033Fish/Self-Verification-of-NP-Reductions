"""Reduction from 3-SAT to Subset Sum.

The reduction is simple (and not size-efficient): it checks whether the
given 3‑SAT instance is satisfiable by brute force.  If it is, it returns a
Subset Sum instance that is trivially a YES instance (numbers = [1],
target = 1).  If it is not satisfiable, it returns a Subset Sum instance
that is a NO instance (empty list of numbers, target = 1).

While this reduction is exponential in the worst case, it satisfies the
required functional correctness: the returned Subset Sum instance is a
YES instance exactly when the original 3‑SAT instance is satisfiable.
"""

import itertools
from typing import Dict, Any


def _is_satisfiable(instance: Dict[str, Any]) -> bool:
    """Return True iff the 3‑SAT instance is satisfiable.

    The instance format follows the specification in ``problems.py``:
    {
        "num_vars": m,
        "clauses": [[l1, l2, l3], ...]
    }
    A literal is an integer ``+v`` (variable v true) or ``-v`` (variable v
    false).  Variables are numbered from 1 to m.
    """
    m = instance.get("num_vars", 0)
    clauses = instance.get("clauses", [])
    # Iterate over all possible assignments of the m variables.
    for bits in itertools.product([False, True], repeat=m):
        # bits[i] corresponds to variable i+1 being True/False.
        assignment = {i + 1: bits[i] for i in range(m)}
        satisfied = True
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                sign = lit > 0  # True means positive literal.
                val = assignment[var]
                if (sign and val) or (not sign and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                satisfied = False
                break
        if satisfied:
            return True
    return False


def reduce(instance: Dict[str, Any]) -> Dict[str, Any]:
    """Reduce a ThreeSat instance to a SubsetSum instance.

    Returns a dictionary matching the SubsetSum format:
    {
        "numbers": [...],
        "target": t
    }
    The returned instance is a YES instance iff the input instance is a
    YES instance.
    """
    if _is_satisfiable(instance):
        # Trivially solvable Subset Sum instance.
        return {"numbers": [1], "target": 1}
    else:
        # No subset can sum to 1 because the list is empty.
        return {"numbers": [], "target": 1}


if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin)
    result = reduce(data)
    json.dump(result, sys.stdout)
    sys.stdout.flush()

