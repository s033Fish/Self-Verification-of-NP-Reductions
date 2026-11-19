import itertools
import json
import sys

# Import problem classes and reduction
from problems import VertexCover, DominatingSet
from reduce import reduce

def main():
    # We'll test all instances up to scale 3 (small) for feasibility.
    scale = 3
    total = 0
    passed = 0
    for instance in VertexCover.enumerate_instances(scale):
        total += 1
        src_yes = VertexCover.is_yes(instance)
        red = reduce(instance)
        tgt_yes = DominatingSet.is_yes(red)
        if src_yes == tgt_yes:
            passed += 1
        else:
            print("Mismatch!", instance, src_yes, tgt_yes, file=sys.stderr)
            # Show reduced instance for debugging
            print(json.dumps(red), file=sys.stderr)
            break
    print(json.dumps({"total": total, "passed": passed}))
    sys.exit(0 if total == passed else 1)

if __name__ == "__main__":
    main()
