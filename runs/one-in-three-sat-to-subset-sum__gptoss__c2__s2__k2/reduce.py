import math

def reduce(instance):
    """Reduce OneInThreeSat instance to SubsetSum instance.
    The reduction encodes each variable as a number whose base-4 digits
    indicate in which clauses the variable appears. The target number has a
    1 in each clause digit, enforcing exactly one true variable per clause.
    """
    m = instance.get("num_vars", 0)
    clauses = instance.get("clauses", [])
    k = len(clauses)
    B = 4  # base larger than max literals per clause (3) to avoid carries
    # accumulate contribution for each variable (1-indexed)
    var_contrib = [0] * (m + 1)
    for idx, clause in enumerate(clauses):
        weight = B ** idx
        for var in clause:
            var_contrib[var] += weight
    # build numbers list, omit zero contributions (variables never appearing)
    numbers = [val for val in var_contrib[1:] if val != 0]
    target = sum(B ** idx for idx in range(k))
    return {"numbers": numbers, "target": target}

# If run as script, simple test
if __name__ == "__main__":
    import json, sys
    data = json.load(sys.stdin)
    json.dump(reduce(data), sys.stdout)
