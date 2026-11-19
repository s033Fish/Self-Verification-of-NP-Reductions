import sys
from problems import Clique, VertexCover
from reduce import reduce

def main():
    max_scale = 2  # small enough for exhaustive enumeration
    total = 0
    passed = 0
    for inst in Clique.enumerate_instances(max_scale):
        total += 1
        src_yes = Clique.is_yes(inst)
        tgt_inst = reduce(inst)
        tgt_yes = VertexCover.is_yes(tgt_inst)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("FAIL", inst, src_yes, tgt_yes, file=sys.stderr)
    # write verdict
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    import json, pathlib
    pathlib.Path('verdict.json').write_text(json.dumps(verdict))
    print(json.dumps(verdict))

if __name__ == "__main__":
    main()
