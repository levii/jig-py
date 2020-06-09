import os
from typing import List

import fire

from jig.collector.application import SourceCodeCollector
from jig.collector.domain import SourceCode
from jig.visualizer.application import DotTextVisualizer, DependencyTextVisualizer

# とりあえずこのmain.pyファイルのパスをルートとする
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))


class Main:
    def source_codes(self, target_path: str) -> None:
        """
        指定されたパスのPythonソースコード解析結果を表示します。
        ディレクトリを指定した場合は再帰的にPythonファイルを収集し、全てのソースコード
        解析結果を表示します。
        :param target_path: 解析対象のソースファイルまたはディレクトリへのパス
        :return:
        """
        source_codes = self._collect_source_codes(target_path)
        print(source_codes)

    def dependency_text(self, target_path: str) -> None:
        """
        指定されたパスのPythonソースコードを解析し、モジュール依存関係を表示します。
        ディレクトリを指定した場合はそのディレクトリ配下のPythonファイルを再帰的に
        収集して解析します。
        :param target_path: 解析対象のソースファイルまたはディレクトリへのパス
        :return:
        """
        source_codes = self._collect_source_codes(target_path)
        print(
            DependencyTextVisualizer(
                source_codes=source_codes, module_names=["jig"]
            ).visualize()
        )

    def dot_text(self, target_path: str, depth: int = 3) -> None:
        """
        指定されたパスのPythonソースコードを解析し、モジュール依存関係をdot形式で出力します。
        ディレクトリを指定した場合はそのディレクトリ配下のPythonファイルを再帰的に
        収集して解析します。
        :param target_path: 解析対象のソースファイルまたはディレクトリへのパス
        :param depth: モジュールパスのどの深さ（ドットの数）まででグルーピングするかを指定します。（デフォルト=3）
        :return:
        """
        source_codes = self._collect_source_codes(target_path)
        dot = DotTextVisualizer(source_codes=source_codes, module_names=["jig"])

        print(dot.visualize(depth=depth))

    def _collect_source_codes(self, target_path: str) -> List[SourceCode]:
        return SourceCodeCollector(root_path=ROOT_PATH).collect(target_path=target_path)


if __name__ == "__main__":
    fire.Fire(Main)
