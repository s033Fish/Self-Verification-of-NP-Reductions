"""Polynomial-time reduction from Subset Sum to Partition.

Source (Subset Sum): {"numbers": [a1, a2, ...], "target": t}
Target (Partition):  {"numbers": [b1, b2, ...]}

Construction: let S = sum(numbers) and append the single number
b = |S - 2t|.  The resulting multiset can be partitioned into two equal
halves exactly when the original numbers contain a sub-list summing to t.

Proof sketch:
  Let total = S + b.
  * If S >= 2t, then b = S - 2t and total = 2(S - t), so the required
    half is S - t.  A sub-list of the original numbers sums to S - t iff
    its complement sums to t.
  * If S < 2t, then b = 2t - S and total = 2t, so the required half is
    t.  If a sub-list of the originals sums to t we are done.  Otherwise
    any witness must use b; removing b leaves originals summing to
    t - b = S - t, whose complement sums to t.
  This also handles t < 0 (always no), t = 0 (always yes), and the empty
  list correctly.
"""


def reduce(instance):
    numbers = list(instance["numbers"])
    target = instance["target"]
    total = sum(numbers)
    extra = abs(total - 2 * target)
    return {"numbers": numbers + [extra]}
