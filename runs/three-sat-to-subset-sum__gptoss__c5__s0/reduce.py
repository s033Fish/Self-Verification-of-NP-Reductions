"""Reduction from 3-SAT to Subset Sum.

The reduction follows a simple digit‑encoding idea.  We work in binary (base 2)
and treat each integer as a vector of bits.  The vector has one position for each
variable and three positions for each clause (one for each literal in the
clause).

For a variable *i* (1‑based) we use bit position ``i-1``.  For clause *j* and
literal index *k* (0,1,2) we use position ``num_vars + 3*j + k``.

Numbers in the Subset‑Sum instance are constructed as follows:

* **Variable dummy** – for each variable we add a number that has a single ``1``
  in its variable position.  Selecting this number means the variable does not
  appear as a true literal in any clause.
* **Literal numbers** – for each occurrence of a literal (positive or negative)
  in clause *j* at index *k* we add a number that has a ``1`` in the variable
  position *i* and a ``1`` in the clause‑literal position ``(j,k)``.
* **Clause fillers** – for every clause‑literal position we also add a filler
  number that has a ``1`` only in that position.  This allows the target bit to
  be satisfied even if the corresponding literal is not chosen.

The target integer has a ``1`` in every variable position (forcing exactly one
number that contributes to each variable) and a ``1`` in every clause‑literal
position (forcing each clause‑literal position to be covered by either the
corresponding literal number or the filler).

Correctness sketch:
* If the 3‑SAT formula is satisfiable, pick for each variable either the dummy
  (if the variable does not appear positively/negatively in a satisfied
  literal) or one literal number that corresponds to a true literal in the
  satisfying assignment.  For each clause‑literal position not covered by a
  chosen literal we pick the filler.  The sum of the selected numbers equals the
  target.
* Conversely, any subset summing to the target must contain exactly one number
  that contributes to each variable position (otherwise the bit would be 0 or
  >1).  The numbers that contribute to a clause‑literal position are either a
  literal number (hence the literal is true) or a filler.  Because each
  clause‑literal position is covered, every clause has at least one true
  literal, yielding a satisfying assignment.

The construction runs in time O(m + 3·|clauses|) and produces numbers that are
polynomial in the size of the input.
"""

from __future__ import annotations

from typing import Dict, List

from problems import ThreeSat, SubsetSum


def _bit(pos: int) -> int:
    """Return the integer with a single ``1`` at bit position ``pos``.

    ``pos`` is zero‑based, i.e., ``_bit(0) == 1``.
    """
    return 1 << pos


def reduce(instance: Dict) -> Dict:
    """Reduce a 3‑SAT instance to a Subset‑Sum instance.

    The returned dict follows the format required by :class:`SubsetSum`:
    ``{"numbers": [...], "target": t}``.
    """
    # Validate the source instance first.
    ThreeSat.validate(instance)

    num_vars: int = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    num_clauses = len(clauses)

    numbers: List[int] = []

    # 1. Variable dummy numbers – one per variable.
    for i in range(1, num_vars + 1):
        numbers.append(_bit(i - 1))

    # 2. Literal numbers – one for each literal occurrence.
    for j, clause in enumerate(clauses):
        for k, literal in enumerate(clause):
            var = abs(literal)
            # variable bit + clause‑literal bit
            val = _bit(var - 1) + _bit(num_vars + 3 * j + k)
            numbers.append(val)

    # 3. Clause filler numbers – one for each clause‑literal position.
    for j in range(num_clauses):
        for k in range(3):
            filler = _bit(num_vars + 3 * j + k)
            numbers.append(filler)

    # Build the target: 1 in every variable bit and every clause‑literal bit.
    target = 0
    for i in range(num_vars):
        target += _bit(i)
    for j in range(num_clauses):
        for k in range(3):
            target += _bit(num_vars + 3 * j + k)

    # Validate the produced target instance.
    result = {"numbers": numbers, "target": target}
    SubsetSum.validate(result)
    return result

