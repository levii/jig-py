import os
import sys

from jig.collector.application import SourceCodeCollector
from jig.collector.application import collect

if __name__ == "__main__":
    # とりあえずこのmain.pyファイルのパスをルートとする
    root_path = os.path.dirname(os.path.abspath(__file__))

    # result = collect(root_path=root_path, target_path=sys.argv[1])
    # print(result)

    result = SourceCodeCollector(root_path=root_path).collect_directories()
    for i in result:
        print(i.file.path)
        print(i.ast.get_imports())
        print(i.ast.get_class_defs())
        print("\n")
