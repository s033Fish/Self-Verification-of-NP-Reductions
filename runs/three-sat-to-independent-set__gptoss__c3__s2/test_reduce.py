import json
import sys
from problems import ThreeSat, IndependentSet
from reduce import reduce

passed = 0
run = 0
# Use a small scale to keep enumeration reasonable
scale = 3
for instance in ThreeSat.enumerate_instances(scale):
    run += 1
    # Validate source (should be valid)
    try:
        ThreeSat.validate(instance)
    except Exception as e:
        print(f"Source validation failed on instance {instance}: {e}")
        sys.exit(1)
    # Reduce
    target = reduce(instance)
    # Validate target
    try:
        IndependentSet.validate(target)
    except Exception as e:
        print(f"Target validation failed on reduced instance {target}: {e}")
        sys.exit(1)
    # Compare answers
    source_yes = ThreeSat.is_yes(instance)
    target_yes = IndependentSet.is_yes(target)
    if source_yes == target_yes:
        passed += 1
    else:
        print("Mismatch!", instance, "->", target, source_yes, target_yes)
        sys.exit(1)

print(f"Tests run: {run}, passed: {passed}")
with open('verdict.json', 'w') as f:
    json.dump({"verified": passed == run, "tests_run": run, "tests_passed": passed}, f)
