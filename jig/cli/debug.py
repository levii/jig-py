import os
from pathlib import Path
from typing import Optional, List

import fire

from jig.analyzer.domain.dependency.import_dependency import ImportDependencyCollection
from jig.collector.application import SourceCodeCollector
from jig.collector.domain.source_code.source_code import SourceCode
from jig.collector.domain.source_code.source_code_collection import SourceCodeCollection


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
        source_codes = SourceCodeCollection(
            self._collect_source_codes(target_path=target_path, root_path=root_path)
        )

        collection = ImportDependencyCollection.build_from_source_code_collection(
            source_codes
        )
        dependencies = collection.build_module_dependencies()

        for dependency in dependencies:
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
