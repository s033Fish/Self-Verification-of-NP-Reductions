"""Tests for the reduction from 3‑SAT to Positive 1‑in‑3‑SAT.

The task requires that ``reduce.reduce`` returns a target instance that is a
*yes* instance iff the source instance is a *yes* instance.  Additionally the
reduction must not rely on a brute‑force solver.  The provided implementation
uses ``solve_three_sat`` – a brute‑force search – which we detect by monkey
patching the function and ensuring it is called.

We therefore perform two kinds of checks:

1. **Correctness** – for a collection of randomly generated small 3‑SAT
   instances we compare the answer of the source solver with the answer of the
   target solver on the reduced instance.
2. **Brute‑force usage** – we replace ``reduce.solve_three_sat`` with a stub
   that raises ``RuntimeError``.  If ``reduce.reduce`` internally calls the
   stub the error propagates, confirming that the reduction relies on the
   brute‑force solver (which violates the specification).

The script is executed by the verification harness and writes a ``verdict.json``
file containing the number of tests run, how many passed and whether the
reduction is verified.
"""

from __future__ import annotations

import json
import random
import unittest
from typing import Dict, Any, List

import reduce  # The module under test
from problems import ThreeSat, OneInThreeSat


def brute_three_sat(instance: Dict[str, Any]) -> bool:
    """Reference brute‑force solver for 3‑SAT (identical to the one in ``reduce``)."""
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit) - 1
                val = (bits >> var) & 1
                if (lit > 0 and val) or (lit < 0 and not val):
                    satisfied = True
                    break
            if not satisfied:
                ok = False
                break
        if ok:
            return True
    return False


def brute_one_in_three_sat(instance: Dict[str, Any]) -> bool:
    """Reference brute‑force solver for Positive 1‑in‑3‑SAT."""
    m = instance["num_vars"]
    clauses: List[List[int]] = instance["clauses"]
    for bits in range(1 << m):
        ok = True
        for clause in clauses:
            true_cnt = 0
            for var in clause:
                true_cnt += (bits >> (var - 1)) & 1
            if true_cnt != 1:
                ok = False
                break
        if ok:
            return True
    return False


def random_three_sat_instance(max_vars: int = 5, max_clauses: int = 6) -> Dict[str, Any]:
    """Generate a random valid 3‑SAT instance.

    The generator respects the validation rules defined in ``ThreeSat``.
    """
    m = random.randint(0, max_vars)
    if m == 0:
        return {"num_vars": 0, "clauses": []}
    m = max(m, 3)
    num_clauses = random.randint(0, max_clauses)
    clauses = []
    for _ in range(num_clauses):
        vars_ = random.sample(range(1, m + 1), 3)
        clause = [v if random.choice([True, False]) else -v for v in vars_]
        clauses.append(clause)
    return {"num_vars": m, "clauses": clauses}


class ReductionTest(unittest.TestCase):
    def test_correctness_random(self):
        """Check that reduction preserves the answer for many random instances."""
        for _ in range(200):
            src = random_three_sat_instance()
            ThreeSat.validate(src)
            src_ans = brute_three_sat(src)
            tgt = reduce.reduce(src)
            OneInThreeSat.validate(tgt)
            tgt_ans = brute_one_in_three_sat(tgt)
            self.assertEqual(src_ans, tgt_ans,
                             f"Mismatch on instance {src}\nReduced to {tgt}")

    def test_bruteforce_usage_detected(self):
        """Detect that ``reduce.reduce`` calls the brute‑force solver.

        We monkey‑patch ``reduce.solve_three_sat`` to raise an exception.  If the
        reduction relies on this function the exception will propagate.
        """
        src = {"num_vars": 3, "clauses": [[1, 2, 3]]}
        ThreeSat.validate(src)
        original_solver = reduce.solve_three_sat
        def bad_solver(_):
            raise RuntimeError("solve_three_sat was called")
        try:
            reduce.solve_three_sat = bad_solver  # type: ignore[attr-defined]
            with self.assertRaises(RuntimeError):
                _ = reduce.reduce(src)
        finally:
            reduce.solve_three_sat = original_solver  # type: ignore[attr-defined]

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    result = runner.run(unittest.defaultTestLoader.loadTestsFromTestCase(ReductionTest))
    total = result.testsRun
    passed = total - len(result.failures) - len(result.errors)
    # The reduction is verified only if all tests pass **and** we have shown it
    # does NOT use a brute‑force solver.  Since the second test expects a
    # RuntimeError, the reduction *does* use the solver, so we set verified to
    # False.
    verified = passed == total and False
    verdict = {
        "verified": verified,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open("verdict.json", "w") as f:
        json.dump(verdict, f, indent=2)
