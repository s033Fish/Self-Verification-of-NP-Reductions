"""Polynomial-time reduction from Subset Sum to Partition.

Source instance: {"numbers": [a1, a2, ...], "target": t}
Target instance: {"numbers": [a1, a2, ...]}

Let S = sum(numbers).  Add one extra number

    x = abs(S - 2*t)

and return {"numbers": numbers + [x]}.

Why this works
--------------
Write A for the original list and consider P = A + [x].

* If t < 0, then x = S - 2t and the total of P is 2*(S - t), so each
  partition group would need sum S - t.  The group not containing x would
  need a subset of A of sum S - t > S, impossible; the group containing x
  would need a subset of A of sum t < 0, also impossible.  Hence P is no,
  matching Subset Sum.

* If t > S, then x = 2t - S and the total of P is 2t, so each group would
  need sum t.  The group not containing x would need a subset of A of sum
  t > S, impossible; the group containing x would need x plus a subset of A
  to equal t, i.e. a subset of sum S - t < 0, also impossible.  Hence P is
  no, matching Subset Sum.

* If 0 <= t <= S, then x = abs(S - 2t) and the total of P is
  S + |S - 2t|, which is even.  Its half is max(S - t, t).
    - If some subset B of A has sum t, then either B (when t is the larger
      half) or A \ B (when S - t is the larger half) gives one partition
      group, and the rest of P gives the other.
    - Conversely, in any equal partition of P, the group not containing x
      has sum equal to the half; if that half is t we are done, and if it is
      S - t then its complement in A has sum t.
  Thus P is yes exactly when some subset of A sums to t.

The extra number has O(size of the input) bits, so the construction runs in
polynomial time and does not solve either problem.
"""


def reduce(instance):
    """Reduce a Subset Sum instance to a Partition instance."""
    numbers = instance["numbers"]
    target = instance["target"]
    extra = abs(sum(numbers) - 2 * target)
    return {"numbers": list(numbers) + [extra]}
