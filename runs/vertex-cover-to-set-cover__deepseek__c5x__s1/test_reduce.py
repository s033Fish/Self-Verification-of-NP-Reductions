import json
import itertools
import sys
from pathlib import Path

# Import problem definitions and reduction
import problems
from reduce import reduce as reduction

# Import our brute-force solvers
from vc_solver import vertex_cover_bruteforce
from setcover_solver import set_cover_bruteforce


def generate_instances(max_n=5):
    instances = []
    for n in range(max_n + 1):
        vertices = list(range(n))
        # all possible edges (undirected, no loops)
        all_edges = [(u, v) for u in vertices for v in vertices if u < v]
        for edge_subset in itertools.chain.from_iterable(itertools.combinations(all_edges, r) for r in range(len(all_edges) + 1)):
            edges = [list(e) for e in edge_subset]
            for k in range(-1, n + 2):  # include some out of range
                instance = {"n": n, "edges": edges, "k": k}
                # validate
                try:
                    problems.VertexCover.validate(instance)
                except Exception as e:
                    # skip invalid (shouldn't happen)
                    continue
                instances.append(instance)
    return instances


def main():
    instances = generate_instances(4)  # keep total manageable
    total = len(instances)
    passed = 0
    for idx, inst in enumerate(instances):
        # compute answers
        ans_vc = vertex_cover_bruteforce(inst)
        reduced = reduction(inst)
        # validate reduced instance
        try:
            problems.SetCover.validate(reduced)
        except Exception as e:
            print(f"Reduced instance invalid for original {inst}: {e}", file=sys.stderr)
            continue
        ans_sc = set_cover_bruteforce(reduced)
        if ans_vc == ans_sc:
            passed += 1
        else:
            print("Mismatch!", file=sys.stderr)
            print("Original:", json.dumps(inst), file=sys.stderr)
            print("Reduced:", json.dumps(reduced), file=sys.stderr)
            print("VC answer:", ans_vc, "SC answer:", ans_sc, file=sys.stderr)
    result = {"verified": passed == total, "tests_run": total, "tests_passed": passed}
    Path("verdict.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result))

if __name__ == "__main__":
    main()
