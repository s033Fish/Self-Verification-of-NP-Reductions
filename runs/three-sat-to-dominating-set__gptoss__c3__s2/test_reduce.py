import random
import json
from problems import ThreeSat, DominatingSet
from reduce import reduce

random.seed(0)

passed = 0
failed = 0
# generate a mixture of random instances
for scale in range(1, 6):
    for _ in range(20):
        inst = ThreeSat.random_instance(random.Random(random.randint(0, 1000000)), scale)
        # compute answers
        src_yes = ThreeSat.is_yes(inst)
        tgt_inst = reduce(inst)
        DominatingSet.validate(tgt_inst)
        tgt_yes = DominatingSet.is_yes(tgt_inst)
        if src_yes == tgt_yes:
            passed += 1
        else:
            failed += 1
            print("Mismatch!", inst, src_yes, tgt_yes)

# edge cases
edge_cases = [
    {"num_vars": 0, "clauses": []},
    {"num_vars": 3, "clauses": []},
]
for inst in edge_cases:
    src_yes = ThreeSat.is_yes(inst)
    tgt_inst = reduce(inst)
    DominatingSet.validate(tgt_inst)
    tgt_yes = DominatingSet.is_yes(tgt_inst)
    if src_yes == tgt_yes:
        passed += 1
    else:
        failed += 1
        print("Mismatch edge", inst, src_yes, tgt_yes)

print(f"Passed: {passed}, Failed: {failed}")

verdict = {
    "verified": failed == 0,
    "tests_run": passed + failed,
    "tests_passed": passed,
}
with open('verdict.json', 'w') as f:
    json.dump(verdict, f)
