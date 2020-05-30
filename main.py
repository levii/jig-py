import os
import sys

from jig.collector.application import SourceCodeCollector
from jig.visualizer.application import DependencyTextVisualizer


def main():
    # とりあえずこのmain.pyファイルのパスをルートとする
    root_path = os.path.dirname(os.path.abspath(__file__))

    source_codes = SourceCodeCollector(root_path=root_path).collect(target_path=sys.argv[1])
    print(source_codes)

    # print(.module_dependencies(["jig"]))
    for source_code in source_codes:
        print(
            DependencyTextVisualizer(
                source_code=source_code, module_names=["jig"]
            ).visualize()
        )


if __name__ == "__main__":
    main()
