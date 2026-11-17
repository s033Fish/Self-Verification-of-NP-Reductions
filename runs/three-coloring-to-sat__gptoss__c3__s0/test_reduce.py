import random
import sys
from problems import ThreeColoring, Sat
from reduce import reduce

def run_tests():
    total = 0
    passed = 0
    # Edge case tests
    edge_cases = []
    # n=0
    edge_cases.append({"n": 0, "edges": []})
    # n=1, no edges
    edge_cases.append({"n": 1, "edges": []})
    # n=3, triangle (3-cycle) which is 3-colorable
    edge_cases.append({"n": 3, "edges": [[0,1],[1,2],[2,0]]})
    # K4 (4 vertices fully connected) -> not 3-colorable
    k4_edges = []
    for i in range(4):
        for j in range(i+1,4):
            k4_edges.append([i,j])
    edge_cases.append({"n": 4, "edges": k4_edges})

    for inst in edge_cases:
        total += 1
        try:
            src_yes = ThreeColoring.is_yes(inst)
            sat_inst = reduce(inst)
            Sat.validate(sat_inst)
            tgt_yes = Sat.is_yes(sat_inst)
            if src_yes == tgt_yes:
                passed += 1
            else:
                print("Mismatch on edge case", inst, src_yes, tgt_yes, file=sys.stderr)
        except Exception as e:
            print("Error on edge case", inst, e, file=sys.stderr)

    # Random small instances
    rng = random.Random(0)
    for scale in range(1,6):  # up to 5 vertices
        for _ in range(50):
            inst = ThreeColoring.random_instance(rng, scale)
            total += 1
            try:
                src_yes = ThreeColoring.is_yes(inst)
                sat_inst = reduce(inst)
                Sat.validate(sat_inst)
                tgt_yes = Sat.is_yes(sat_inst)
                if src_yes == tgt_yes:
                    passed += 1
                else:
                    print("Mismatch", inst, src_yes, tgt_yes, file=sys.stderr)
            except Exception as e:
                print("Error", inst, e, file=sys.stderr)
    return total, passed

if __name__ == "__main__":
    total, passed = run_tests()
    print(f"Tests run: {total}, passed: {passed}")
    sys.exit(0 if total == passed else 1)
