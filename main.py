import os
import sys

from jig.collector.application import collect
from jig.visualizer.application import DependencyTextVisualizer


def main():
    # とりあえずこのmain.pyファイルのパスをルートとする
    root_path = os.path.dirname(os.path.abspath(__file__))

    source_code = collect(root_path=root_path, target_path=sys.argv[1])
    print(source_code)

    print(source_code.module_dependencies(["jig"]))
    print(DependencyTextVisualizer(source_code=source_code, module_names=["jig"]).visualize())


if __name__ == "__main__":
    main()
