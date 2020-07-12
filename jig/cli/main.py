import os
from pathlib import Path

import fire

from jig.analizer.application import ModuleDependencyAnalyzer
from jig.analizer.domain import SourceCodeList
from jig.collector.application import SourceCodeCollector
from jig.visualizer.application import ModuleDependencyVisualizer


def _collect_source_codes(target_path: str) -> SourceCodeList:
    root_path = os.getcwd()

    source_code_list = list(
        SourceCodeCollector(root_path=Path(root_path)).collect(
            target_path=Path(target_path)
        )
    )
    return SourceCodeList(_source_codes=source_code_list)


def output_dependency_images(target_path, output_dir="output"):
    """
    指定されたディレクトリ以下を解析し、その結果を出力ディレクトリに出力します。
    各Pythonファイルのモジュール名は、実行時のカレントディレクトリをPYTHONPATHとして解釈されます。
    :param target_path: 解析対象のパスを指定します。
    :param output_dir: 解析結果の出力ディレクトリを指定します（デフォルト: output）
    :return:
    """

    for depth in range(1, 8):
        source_codes = _collect_source_codes(target_path=target_path)

        analyzer = ModuleDependencyAnalyzer(source_code_list=source_codes)
        dependencies = analyzer.analyze()

        visualizer = ModuleDependencyVisualizer(dependencies=dependencies)
        visualizer.visualize(depth=depth, output_dir=output_dir)
        visualizer.render_dot_text(depth=depth, output_dir=output_dir)


def main():
    fire.Fire(output_dependency_images)


if __name__ == "__main__":
    main()
