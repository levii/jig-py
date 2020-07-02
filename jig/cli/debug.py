import os
from pathlib import Path
from typing import Optional, List

import fire

from jig.collector.application import SourceCodeCollector
from jig.collector.domain import SourceCode
from jig.visualizer.application import (
    DependencyTextVisualizer,
    DotTextVisualizer,
    DependencyImageVisualizer,
)


class Main:
    def source_codes(self, target_path: str, root_path: Optional[str] = None) -> None:
        """
        指定されたパスのPythonソースコード解析結果を表示します。
        ディレクトリを指定した場合は再帰的にPythonファイルを収集し、全てのソースコード
        解析結果を表示します。
        :param target_path: 解析対象のソースファイルまたはディレクトリへのパス
        :param root_path: 解析対象Pythonコードのルートディレクトリパス
        :return:
        """
        source_codes = self._collect_source_codes(
            target_path=target_path, root_path=root_path
        )
        print(source_codes)

    def dependency_text(
        self,
        target_path: str,
        root_path: Optional[str] = None,
        module_names: List[str] = None,
    ) -> None:
        """
        指定されたパスのPythonソースコードを解析し、モジュール依存関係を表示します。
        ディレクトリを指定した場合はそのディレクトリ配下のPythonファイルを再帰的に
        収集して解析します。
        :param target_path: 解析対象のソースファイルまたはディレクトリへのパス
        :param root_path: 解析対象Pythonコードのルートディレクトリパス
        :param module_names: 出力結果に含めるモジュールのパスプレフィックス。"jig"を指定した場合、"jig.xxx.yyy" といった
                             モジュールだけが結果に含まれるようになります。複数指定したい場合は配列形式で指定します。
                             （例: --module_names "[jig, os]"）
        :return:
        """
        source_codes = self._collect_source_codes(
            target_path=target_path, root_path=root_path
        )
        print(
            DependencyTextVisualizer(
                source_codes=source_codes, module_names=module_names or []
            ).visualize()
        )

    def dot_text(
        self,
        target_path: str,
        root_path: Optional[str] = None,
        module_names: List[str] = None,
        depth: int = 3,
    ) -> None:
        """
        指定されたパスのPythonソースコードを解析し、モジュール依存関係をdot形式で出力します。
        ディレクトリを指定した場合はそのディレクトリ配下のPythonファイルを再帰的に
        収集して解析します。
        :param target_path: 解析対象のソースファイルまたはディレクトリへのパス
        :param root_path: 解析対象Pythonコードのルートディレクトリパス
        :param module_names: 出力結果に含めるモジュールのパスプレフィックス。"jig"を指定した場合、"jig.xxx.yyy" といった
                             モジュールだけが結果に含まれるようになります。複数指定したい場合は配列形式で指定します。
                             （例: --module_names "[jig, os]"）
        :param depth: モジュールパスのどの深さ（ドットの数）まででグルーピングするかを指定します。（デフォルト=3）
        :return:
        """
        source_codes = self._collect_source_codes(
            target_path=target_path, root_path=root_path
        )
        dot = DotTextVisualizer(
            source_codes=source_codes, module_names=module_names or []
        )

        print(dot.visualize(depth=depth))

    def module_dependency(
        self,
        target_path: str,
        root_path: Optional[str] = None,
        module_names: List[str] = None,
        depth: int = 3,
        output_dir: str = "./output",
    ) -> None:
        """
        指定されたパスのPythonソースコードを解析し、モジュール依存関係をpng形式の画像として出力します。
        ディレクトリを指定した場合はそのディレクトリ配下のPythonファイルを再帰的に収集して解析します。
        :param target_path: 解析対象のソースファイルまたはディレクトリへのパス
        :param root_path: 解析対象Pythonコードのルートディレクトリパス（デフォルト=実行時のカレントディレクトリ）
        :param module_names: 出力結果に含めるモジュールのパスプレフィックス。"jig"を指定した場合、"jig.xxx.yyy" といった
                             モジュールだけが結果に含まれるようになります。複数指定したい場合は配列形式で指定します。
                             （例: --module_names "[jig, os]"）
        :param depth: モジュールパスのどの深さ（ドットの数）まででグルーピングするかを指定します。（デフォルト=3）
        :param output_dir: 出力先ディレクトリ。（デフォルト=./output）
        :return:
        """
        if isinstance(module_names, str):
            module_names = [module_names]

        source_codes = self._collect_source_codes(
            target_path=target_path, root_path=root_path
        )
        dot = DependencyImageVisualizer(
            source_codes=source_codes, module_names=module_names or []
        )

        dot.visualize(depth=depth, output_dir=output_dir)

    def _collect_source_codes(
        self, target_path: str, root_path: Optional[str]
    ) -> List[SourceCode]:
        if not root_path:
            root_path = os.getcwd()

        return list(
            SourceCodeCollector(root_path=Path(root_path)).collect(
                target_path=Path(target_path)
            )
        )


def main():
    fire.Fire(Main)


if __name__ == "__main__":
    main()
