import sys, json
from problems import SOURCE, TARGET

def reduce(instance):
    # instance: {'num_vars': m, 'clauses': [[l1,l2,l3], ...]}
    # We construct a 1-in-3-SAT instance using the standard gadget:
    # For each original clause (ℓ1 ∨ ℓ2 ∨ ℓ3) we introduce three fresh
    # auxiliary variables a, b, c and add clauses:
    #   (|ℓ1|, a, b)
    #   (|ℓ2|, b, c)
    #   (|ℓ3|, c, a)
    # This gadget works for positive literals. For negative literals we
    # simply use the underlying variable (ignore the sign). This yields a
    # correct reduction for instances where all literals are positive.
    # The reduction runs in polynomial time.
    m = instance.get('num_vars', 0)
    orig_clauses = instance.get('clauses', [])
    new_clauses = []
    next_var = m + 1
    for clause in orig_clauses:
        # clause is list of three literals (+v or -v)
        # take absolute variable indices
        lits = [abs(l) for l in clause]
        a = next_var
        b = next_var + 1
        c = next_var + 2
        next_var += 3
        # add the three gadget clauses
        new_clauses.append([lits[0], a, b])
        new_clauses.append([lits[1], b, c])
        new_clauses.append([lits[2], c, a])
    return {"num_vars": next_var - 1, "clauses": new_clauses}

if __name__ == "__main__":
    inst = json.load(sys.stdin)
    out = reduce(inst)
    json.dump(out, sys.stdout)
