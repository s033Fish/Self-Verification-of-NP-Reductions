"""Polynomial-time reduction from Exact Cover to Subset Sum.

Idea (standard positional / base encoding)
------------------------------------------
Let the universe be 0..u-1 and the sets be S_0..S_{m-1}.  Pick a base
b > m (e.g. b = max(m+1, 2)).  Represent a collection of sets by the
integer

    sum over chosen sets j of  ( sum over e in S_j of b^e ).

In base b, the digit in position e counts how many chosen sets contain
element e.  Since at most m sets can be chosen, every digit is at most
m < b, so there are no carries and the base-b digit representation is
exact.  The target

    t = sum_{e=0}^{u-1} b^e

has digit 1 in every universe position.  A sub-list of the produced
numbers sums to t iff the corresponding sets cover every element exactly
once, i.e. iff the Exact Cover instance is a yes-instance.

Empty sets become the number 0 (harmless: adding 0 changes nothing), and
duplicate sets become equal numbers, so choosing two copies would put a
digit 2 in some position and cannot reach the target.

The numbers produced have O(u * log m) bits each and there are m of them,
so the whole reduction runs in time polynomial in the input size.
"""

from __future__ import annotations


def reduce(instance):
    """Reduce an ExactCover instance to a SubsetSum instance."""
    universe_size = instance["universe_size"]
    sets = instance["sets"]
    num_sets = len(sets)

    # Base strictly larger than the number of sets guarantees no carries.
    base = max(num_sets + 1, 2)

    # Precompute powers b^e for e in 0..u-1.
    powers = [base ** e for e in range(universe_size)]

    numbers = []
    for subset in sets:
        value = 0
        for element in subset:
            value += powers[element]
        numbers.append(value)

    target = sum(powers)

    return {"numbers": numbers, "target": target}
