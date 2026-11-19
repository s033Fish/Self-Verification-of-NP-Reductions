import json
import itertools
import sys
from problems import Clique, VertexCover
from reduce import reduce
from solve_bruteforce import solve_clique, solve_vertex_cover

def generate_instances(max_n=5):
    for n in range(max_n + 1):
        vertices = list(range(n))
        all_pairs = list(itertools.combinations(vertices, 2))
        # iterate over all subsets of edges
        for edges_mask in range(1 << len(all_pairs)):
            edges = []
            for i, (u, v) in enumerate(all_pairs):
                if (edges_mask >> i) & 1:
                    edges.append([u, v])
            for k in range(-1, n + 2):  # include some out of range values
                instance = {"n": n, "edges": edges, "k": k}
                # validate instance for Clique (should be same format as VertexCover)
                try:
                    Clique.validate(instance)
                except Exception as e:
                    # invalid instance according to spec, skip
                    continue
                yield instance

def main():
    total = 0
    passed = 0
    for inst in generate_instances():
        total += 1
        # compute answers
        ans_clique = solve_clique(inst)
        red = reduce(inst)
        # validate reduced instance for VertexCover
        try:
            VertexCover.validate(red)
        except Exception as e:
            print("Reduced instance invalid", red, file=sys.stderr)
            continue
        ans_vc = solve_vertex_cover(red)
        if ans_clique == ans_vc:
            passed += 1
        else:
            print("Mismatch!", inst, red, ans_clique, ans_vc, file=sys.stderr)
    verdict = {
        "verified": passed == total,
        "tests_run": total,
        "tests_passed": passed,
    }
    with open('verdict.json', 'w') as f:
        json.dump(verdict, f, indent=2)
    print(json.dumps(verdict, indent=2))

if __name__ == "__main__":
    main()
