import sys
from problems import SubsetSum, Sat
from reduce import reduce

def main():
    total = 0
    passed = 0
    # Use a modest scale to keep runtime low
    for scale in range(0, 4):
        for instance in SubsetSum.enumerate_instances(scale):
            total += 1
            try:
                subset_yes = SubsetSum.is_yes(instance)
                sat_instance = reduce(instance)
                sat_yes = Sat.is_yes(sat_instance)
                if subset_yes == sat_yes:
                    passed += 1
                else:
                    print("Mismatch!", instance, sat_instance, subset_yes, sat_yes, file=sys.stderr)
            except Exception as e:
                print("Error on instance", instance, e, file=sys.stderr)
    print({"tests_run": total, "tests_passed": passed})
    if passed != total:
        sys.exit(1)

if __name__ == "__main__":
    main()
