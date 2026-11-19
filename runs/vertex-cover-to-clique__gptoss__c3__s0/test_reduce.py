import traceback
from problems import VertexCover, Clique
import reduce

def run_tests():
    total = 0
    passed = 0
    # enumerate a reasonable number of instances (scale up to 4)
    for inst in VertexCover.enumerate_instances(4):
        total += 1
        try:
            src_ans = VertexCover.is_yes(inst)
            red = reduce.reduce(inst)
            tgt_ans = Clique.is_yes(red)
            if src_ans == tgt_ans:
                passed += 1
            else:
                print('FAIL mismatch', inst, src_ans, tgt_ans)
        except Exception as e:
            print('FAIL exception', inst)
            traceback.print_exc()
    # Additional explicit edge cases
    edge_cases = [
        {"n": 5, "edges": [], "k": -1},
        {"n": 5, "edges": [], "k": 0},
        {"n": 5, "edges": [], "k": 5},
        {"n": 5, "edges": [], "k": 10},
        {"n": 3, "edges": [[0,1],[1,2]], "k": -2},
        {"n": 3, "edges": [[0,1],[1,2]], "k": 3},
    ]
    for inst in edge_cases:
        total += 1
        try:
            src_ans = VertexCover.is_yes(inst)
            red = reduce.reduce(inst)
            tgt_ans = Clique.is_yes(red)
            if src_ans == tgt_ans:
                passed += 1
            else:
                print('FAIL edge case', inst, src_ans, tgt_ans)
        except Exception as e:
            print('FAIL edge case exception', inst)
            traceback.print_exc()
    return total, passed

if __name__ == '__main__':
    total, passed = run_tests()
    print(f'Tests run: {total}, passed: {passed}')
