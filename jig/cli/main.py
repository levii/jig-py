from pathlib import Path

import fire

from jig.analyzer.domain.dependency.import_dependency import ImportDependencyCollection
from jig.collector.application import SourceCodeCollector
from jig.collector.domain.source_code.source_code_collection import SourceCodeCollection
from jig.visualizer.application import ModuleDependencyVisualizer


def _collect_source_codes(project_root_path: str) -> SourceCodeCollection:
    return SourceCodeCollector(root_path=Path(project_root_path)).collect(
        target_path=Path(project_root_path)
    )


def output_dependency_images(project_root_path, output_dir="output"):
    """
    指定されたディレクトリ以下を解析し、その結果を出力ディレクトリに出力します。
    :param project_root_path: 解析対象プロジェクトのプロジェクトルートパスを指定します。
    :param output_dir: 解析結果の出力ディレクトリを指定します（デフォルト: output）
    :return:
    """

    for depth in range(1, 8):
        source_codes = _collect_source_codes(project_root_path=project_root_path)

        collection = ImportDependencyCollection.build_from_source_code_collection(
            source_codes
        )
        dependencies = collection.build_module_dependencies()

        visualizer = ModuleDependencyVisualizer(dependencies=dependencies)
        visualizer.visualize(depth=depth, output_dir=output_dir)
        visualizer.render_dot_text(depth=depth, output_dir=output_dir)


def main():
    fire.Fire(output_dependency_images)


if __name__ == "__main__":
    main()
