import sys

from jig.collector.application import collect

if __name__ == "__main__":
    result = collect(target_path=sys.argv[1])
    print(result)
