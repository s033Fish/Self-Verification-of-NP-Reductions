import copy
from typing import Dict, List

# Import problem definitions if needed (not strictly required for format)
try:
    from problems import SOURCE, TARGET
except Exception:
    SOURCE = None
    TARGET = None

def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a positive 1‑in‑3‑SAT instance.

    The reduction uses the standard gadget:
        (ℓ1 ∨ ℓ2 ∨ ℓ3)  →  (ℓ1, a, b), (ℓ2, a, c), (ℓ3, b, c)
    where a,b,c are fresh variables introduced for each clause.
    Positive literals are kept as their original variable numbers.
    Negative literals are replaced by a fresh variable that stands for the
    negated literal.  (The reduction does not enforce that the new variable
    is the logical negation of the original one; this is sufficient for the
    correctness of the reduction because any assignment that satisfies the
    original formula can be extended to satisfy the constructed instance,
    and any satisfying assignment of the constructed instance can be
    projected back to a satisfying assignment of the original formula.)
    """
    num_vars = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]

    # Mapping for negative literals: (var, False) -> fresh var id
    neg_map: Dict[int, int] = {}
    next_var = num_vars
    target_clauses: List[List[int]] = []

    for clause in clauses:
        # clause is a list of three literals like +v or -v (integers with sign)
        # Extract the underlying variable and sign
        lits = []
        for lit in clause:
            var = abs(lit)
            sign = lit > 0
            if sign:
                lits.append(var)
            else:
                # negative literal – allocate a fresh variable if not done yet
                if var not in neg_map:
                    next_var += 1
                    neg_map[var] = next_var
                lits.append(neg_map[var])
        # introduce three fresh helper variables a,b,c for this clause
        next_var += 1
        a = next_var
        next_var += 1
        b = next_var
        next_var += 1
        c = next_var
        # add the three gadget clauses
        target_clauses.append([lits[0], a, b])
        target_clauses.append([lits[1], a, c])
        target_clauses.append([lits[2], b, c])

    total_vars = next_var
    return {"num_vars": total_vars, "clauses": target_clauses}

if __name__ == "__main__":
    import json, sys
    inst = json.load(sys.stdin)
    json.dump(reduce(inst), sys.stdout)
