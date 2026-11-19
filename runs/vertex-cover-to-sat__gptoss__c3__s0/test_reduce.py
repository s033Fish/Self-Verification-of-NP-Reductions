import sys
from problems import VertexCover, Sat
from reduce import reduce

def main():
    total = 0
    passed = 0
    # Enumerate all instances with scale up to 3 (small)
    for instance in VertexCover.enumerate_instances(3):
        total += 1
        vc_yes = VertexCover.is_yes(instance)
        sat_instance = reduce(instance)
        sat_yes = Sat.is_yes(sat_instance)
        if vc_yes == sat_yes:
            passed += 1
        else:
            print("Mismatch!", instance, vc_yes, sat_yes, sat_instance, file=sys.stderr)
    print(f"{passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
