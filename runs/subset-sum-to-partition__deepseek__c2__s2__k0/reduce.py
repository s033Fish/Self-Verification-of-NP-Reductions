"""Polynomial-time reduction from Subset Sum to Partition.

Source instance (Subset Sum):
    {"numbers": [a1, a2, ...], "target": t}
Target instance (Partition):
    {"numbers": [a1, a2, ...]}

Construction
------------
Let S = sum(numbers).  Append the single number

    b = abs(S - 2 * t)

and output {"numbers": numbers + [b]}.

Why it is correct
-----------------
The new total is S + b and a valid partition needs a subset summing to
(S + b) / 2.

* t < 0: b = S - 2t, so the new total is 2(S - t) and the required half is
  S - t > S.  No subset of the original numbers can reach it, and adding b
  only overshoots, so the Partition instance is "no" -- matching t < 0.

* 0 <= t <= S/2: b = S - 2t >= 0, total = 2(S - t), half = S - t.
  A group summing to S - t either contains b, forcing the rest of that group
  to sum to t, or does not, in which case its complement (containing b) sums
  to t.  Hence Partition is "yes" iff some subset sums to t.

* S/2 < t <= S: b = 2t - S >= 0, total = 2t, half = t.  A group summing to
  t either excludes b (a subset sums to t) or includes b (the rest sums to
  S - t, which exists iff a subset sums to t, by complementation).  Hence
  Partition is "yes" iff some subset sums to t.

* t > S: b = 2t - S > t, so a group summing to t cannot contain b, and
  without b no subset of the original numbers reaches t > S.  Partition is
  "no", matching Subset Sum.

* t = 0: b = S, total = 2S, half = S, always achievable (all originals vs b),
  matching the always-yes edge case.

Zeros and the empty list are handled by the same formula.  The construction
uses only a sum and an absolute value, so it runs in linear (polynomial) time
and never calls a solver.
"""


def reduce(instance):
    """Return a Partition instance yes iff the Subset Sum instance is yes."""
    numbers = instance["numbers"]
    target = instance["target"]
    total = sum(numbers)
    extra = abs(total - 2 * target)
    return {"numbers": list(numbers) + [extra]}
