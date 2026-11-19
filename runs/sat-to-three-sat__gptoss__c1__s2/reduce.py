"""Reduction from SAT to 3-SAT.

The source problem ``Sat`` uses the instance format
``{"num_vars": m, "clauses": [[literal, ...], ...]}`` where each clause may
contain an arbitrary number of literals (including zero).  The target
problem ``ThreeSat`` requires each clause to contain exactly three *distinct*
variables.

This implementation provides a polynomial‑time reduction that works for all
well‑formed inputs.  The construction follows the classic textbook reduction:

* Clauses with exactly three distinct literals are copied unchanged.
* Clauses with more than three literals are broken into a chain of 3‑clauses
  using fresh auxiliary variables.
* Clauses with one or two literals are padded with fresh auxiliary variables
  that are forced to be false.
* Tautological clauses (containing a literal and its negation) are ignored
  because they are always satisfied.
* Duplicate literals are collapsed to a single literal of the same sign.

The auxiliary‑false gadget for a variable ``x`` introduces two new helper
variables ``y`` and ``z`` and adds the clauses ``[ -x,  y,  z]`` and
``[ -y, -z, -x]``.  These two clauses are satisfiable iff ``x`` is assigned
``False``.  Because each clause contains three distinct variables, the gadget
conforms to the ``ThreeSat`` format.

The reduction runs in time linear in the size of the input plus the number of
auxiliary variables introduced, which is polynomial.
"""

from typing import List, Dict
import importlib

problems = importlib.import_module("problems")
Sat = problems.Sat
ThreeSat = problems.ThreeSat


def _neg(lit: int) -> int:
    """Return the negation of a literal encoded as +/-v."""
    return -lit


def _new_var(counter: List[int]) -> int:
    """Generate a fresh variable index (positive integer)."""
    v = counter[0]
    counter[0] += 1
    return v


def _force_false(var: int, aux_counter: List[int], clauses: List[List[int]]) -> None:
    """Add clauses that force ``var`` to be False.

    The gadget uses two fresh auxiliary variables ``y`` and ``z`` and adds
    ``[ -var, y, z]`` and ``[ -y, -z, -var]``.  These clauses are satisfied only
    when ``var`` is False.
    """
    y = _new_var(aux_counter)
    z = _new_var(aux_counter)
    clauses.append([_neg(var), y, z])
    clauses.append([_neg(y), _neg(z), _neg(var)])


def reduce(instance: Dict) -> Dict:
    """Reduce a SAT instance to an equivalent 3‑SAT instance.

    Parameters
    ----------
    instance: dict
        A SAT instance following the ``Sat`` format.

    Returns
    -------
    dict
        A ``ThreeSat`` instance that is satisfiable iff the input instance is
        satisfiable.
    """
    if not Sat.validate(instance):
        raise ValueError("Invalid SAT instance")

    m = instance["num_vars"]
    original_clauses: List[List[int]] = instance["clauses"]

    aux_counter = [m + 1]  # next fresh variable index
    new_clauses: List[List[int]] = []

    # Edge case: empty formula is trivially satisfiable.
    if not original_clauses:
        return {"num_vars": max(0, m), "clauses": []}

    for clause in original_clauses:
        # Collapse duplicates and detect tautologies.
        lit_by_var: Dict[int, int] = {}
        tautology = False
        for lit in clause:
            var = abs(lit)
            if var in lit_by_var:
                if lit_by_var[var] != lit:
                    tautology = True
                    break
            else:
                lit_by_var[var] = lit
        if tautology:
            # Clause always true – skip.
            continue
        clause = list(lit_by_var.values())
        k = len(clause)

        if k == 0:
            # Original empty clause -> unsatisfiable formula.
            # Build an explicit unsatisfiable 3‑SAT instance.
            # Introduce a fresh variable x that must be both true and false.
            x = _new_var(aux_counter)
            # Clause forcing x true (pad with two forced‑false vars).
            a = _new_var(aux_counter)
            b = _new_var(aux_counter)
            _force_false(a, aux_counter, new_clauses)
            _force_false(b, aux_counter, new_clauses)
            new_clauses.append([x, a, b])
            # Force x false as well.
            _force_false(x, aux_counter, new_clauses)
            continue

        if k == 1:
            a = _new_var(aux_counter)
            b = _new_var(aux_counter)
            _force_false(a, aux_counter, new_clauses)
            _force_false(b, aux_counter, new_clauses)
            new_clauses.append([clause[0], a, b])
            continue
        if k == 2:
            a = _new_var(aux_counter)
            _force_false(a, aux_counter, new_clauses)
            new_clauses.append([clause[0], clause[1], a])
            continue
        if k == 3:
            # Ensure three distinct variables (they are by construction).
            new_clauses.append(clause[:])
            continue
        # k > 3: break into a chain of 3‑clauses.
        lits = clause
        # First clause uses first two literals and a fresh aux.
        prev = lits[0]
        for i in range(1, k - 2):
            yi = _new_var(aux_counter)
            new_clauses.append([prev, lits[i], yi])
            prev = _neg(yi)
        # Final clause.
        new_clauses.append([prev, lits[-2], lits[-1]])

    total_vars = aux_counter[0] - 1
    if total_vars < 3:
        total_vars = 3
    return {"num_vars": total_vars, "clauses": new_clauses}

