import os
from pathlib import Path
from typing import List

import fire

from jig.collector.application import SourceCodeCollector
from jig.collector.domain import SourceCode
from jig.visualizer.application import DependencyImageVisualizer


def _collect_source_codes(target_path: str) -> List[SourceCode]:
    root_path = os.getcwd()

    return list(
        SourceCodeCollector(root_path=Path(root_path)).collect(
            target_path=Path(target_path)
        )
    )


def output_dependency_images(target_path, output_dir="output"):
    """
    指定されたディレクトリ以下を解析し、その結果を出力ディレクトリに出力します。
    各Pythonファイルのモジュール名は、実行時のカレントディレクトリをPYTHONPATHとして解釈されます。
    :param target_path: 解析対象のパスを指定します。
    :param output_dir: 解析結果の出力ディレクトリを指定します（デフォルト: output）
    :return:
    """
    for depth in range(1, 6):
        source_codes = _collect_source_codes(target_path=target_path)
        dot = DependencyImageVisualizer(source_codes=source_codes, module_names=[])

        dot.visualize(depth=depth, output_dir=output_dir)


def main():
    fire.Fire(output_dependency_images)


if __name__ == "__main__":
    main()
