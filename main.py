import os
import sys

from jig.collector.application import collect

if __name__ == "__main__":
    # とりあえずこのmain.pyファイルのパスをルートとする
    root_path = os.path.dirname(os.path.abspath(__file__))

    result = collect(root_path=root_path, target_path=sys.argv[1])
    print(result)

    print(result.module_dependencies(["jig"]))
