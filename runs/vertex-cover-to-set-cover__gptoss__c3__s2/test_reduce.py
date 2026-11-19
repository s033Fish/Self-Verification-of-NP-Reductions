import json
import random
import sys
from pathlib import Path

import problems
from reduce import reduce

def test_all_enumerated(scale: int) -> tuple[int, int]:
    total = 0
    passed = 0
    for instance in problems.VertexCover.enumerate_instances(scale):
        total += 1
        # Reduce
        reduced = reduce(instance)
        # Validate both (should be valid)
        try:
            problems.VertexCover.validate(instance)
            problems.SetCover.validate(reduced)
        except problems.InvalidInstance as e:
            print("Invalid instance after reduction", e, file=sys.stderr)
            continue
        # Compare answers
        yes_src = problems.VertexCover.is_yes(instance)
        yes_tgt = problems.SetCover.is_yes(reduced)
        if yes_src == yes_tgt:
            passed += 1
        else:
            print("Mismatch!", instance, reduced, yes_src, yes_tgt, file=sys.stderr)
    return total, passed

def test_random(num_trials: int, scale: int) -> tuple[int, int]:
    total = 0
    passed = 0
    rng = random.Random(0)
    for _ in range(num_trials):
        instance = problems.VertexCover.random_instance(rng, scale)
        total += 1
        reduced = reduce(instance)
        # Validate
        problems.VertexCover.validate(instance)
        problems.SetCover.validate(reduced)
        if problems.VertexCover.is_yes(instance) == problems.SetCover.is_yes(reduced):
            passed += 1
        else:
            print("Random mismatch", instance, reduced, file=sys.stderr)
    return total, passed

if __name__ == "__main__":
    total = 0
    passed = 0
    # Small exhaustive test
    t, p = test_all_enumerated(3)
    total += t
    passed += p
    # Random tests
    t, p = test_random(200, 5)
    total += t
    passed += p
    # Write verdict
    verdict = {
        "verified": total == passed,
        "tests_run": total,
        "tests_passed": passed,
    }
    Path("verdict.json").write_text(json.dumps(verdict))
    print(json.dumps(verdict))
