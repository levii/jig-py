import os
from pathlib import Path
from typing import Optional, List

import fire

from jig.analyzer.application import ModuleDependencyAnalyzer
from jig.analyzer.domain import SourceCodeList
from jig.collector.application import SourceCodeCollector
from jig.collector.domain.source_code.source_code import SourceCode
from jig.visualizer.application import (
    DependencyTextVisualizer,
    DotTextVisualizer,
    DependencyImageVisualizer,
)


class Main:
    def modules(self, target_path: str, root_path: Optional[str] = None) -> None:
        """
        指定されたパスのモジュール名を表示します。
        ディレクトリを指定した場合は再帰的にPythonファイルを収集し、全てのソースコード
        のモジュール名をリストで表示します。
        :param target_path: 解析対象のソースファイルまたはディレクトリへのパス
        :param root_path: 解析対象Pythonコードのルートディレクトリパス
        :return:
        """
        source_codes = self._collect_source_codes(
            target_path=target_path, root_path=root_path
        )
        for source_code in source_codes:
            print(str(source_code.module_path))

    def module_imports(self, target_path: str, root_path: Optional[str] = None) -> None:
        """
        指定されたパスのモジュールのインポートしているモジュールリストを表示します。
        ディレクトリを指定した場合は再帰的にPythonファイルを収集し、全てのソースコード
        のモジュールのインポートしているモジュールをリストで表示します。
        :param target_path: 解析対象のソースファイルまたはディレクトリへのパス
        :param root_path: 解析対象Pythonコードのルートディレクトリパス
        :return:
        """
        source_codes = self._collect_source_codes(
            target_path=target_path, root_path=root_path
        )
        for source_code in source_codes:
            for import_module in source_code.import_paths:
                print(str(source_code.module_path), str(import_module.module_path))

    def module_deps(self, target_path: str, root_path: Optional[str] = None) -> None:
        source_codes = self._collect_source_codes(
            target_path=target_path, root_path=root_path
        )
        analyzer = ModuleDependencyAnalyzer(
            source_code_list=SourceCodeList(_source_codes=source_codes)
        )

        for dependency in analyzer.analyze():
            print(str(dependency.src), str(dependency.dest))

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
