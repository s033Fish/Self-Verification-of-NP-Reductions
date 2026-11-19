import problems
from reduce import reduce

def test_sat_to_clique():
    """Run the reduction on a bounded number of SAT instances.

    Enumerating all SAT instances for ``scale=3`` is huge (exponential), so we
    limit the test to the first 200 instances. This is sufficient to catch
    obvious mistakes while keeping the runtime well under the sandbox limit.
    """
    scale = 3
    limit = 200
    total = 0
    passed = 0
    for instance in problems.Sat.enumerate_instances(scale):
        if total >= limit:
            break
        total += 1
        clique_inst = reduce(instance)
        sat_ans = problems.Sat.is_yes(instance)
        clique_ans = problems.Clique.is_yes(clique_inst)
        if sat_ans == clique_ans:
            passed += 1
        else:
            print("Mismatch!", instance, "=>", clique_inst, sat_ans, clique_ans)
            break
    assert total > 0, "No instances generated"
    assert passed == total, f"Only {passed}/{total} instances passed"
    print(f"All {total} instances passed.")

if __name__ == "__main__":
    test_sat_to_clique()
