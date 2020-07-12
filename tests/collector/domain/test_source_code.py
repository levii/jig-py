from pathlib import Path

from jig.collector.domain.source_code.source_code_import_dependency import (
    SourceCodeImportDependency,
)
from jig.collector.domain.values.import_path import ImportPath
from jig.collector.domain.values.import_path_collection import ImportPathCollection
from jig.collector.domain.values.module_path import ModulePath
from jig.collector.domain.source_code.source_code import SourceCode
from jig.collector.domain.source_code.source_code_collection import SourceCodeCollection
from jig.collector.domain.values.module_dependency import ModuleDependency
from jig.collector.domain.source_file.source_file import SourceFile
from jig.collector.domain.source_file.source_file_path import SourceFilePath


class TestSourceCode:
    def test_build(self):
        root_path = "/root"
        main_py = SourceCode.build(
            file=SourceFile(
                source_file_path=SourceFilePath(
                    root_path=Path(root_path), file_path=Path("/root/main.py")
                ),
                size=0,
                content="",
            )
        )
        test_py = SourceCode.build(
            file=SourceFile(
                source_file_path=SourceFilePath(
                    root_path=Path(root_path), file_path=Path("/root/test.py")
                ),
                size=0,
                content="",
            )
        )
        assert isinstance(main_py, SourceCode)
        assert isinstance(test_py, SourceCode)

        collection = SourceCodeCollection([main_py, test_py])
        assert len(collection) == 2
        assert collection.get_by_relative_path("main.py") == main_py
        assert collection.get_by_relative_path("test.py") == test_py

    def test_module_dependencies(self):
        source_file_path = SourceFilePath(
            root_path=Path("/root"), file_path=Path("/root/main.py")
        )
        assert str(source_file_path.module_path) == "main"

        code = SourceCode.build(
            file=SourceFile(
                source_file_path=source_file_path,
                size=100,
                content="from os import path",
            )
        )

        assert code.module_dependencies() == [
            ModuleDependency(
                src=ModulePath.from_str("main"), dest=ModulePath.from_str("os.path")
            )
        ]
        assert code.module_dependencies(module_names=["jig"]) == []

    def test_build_import_dependency(self):
        source_file_path = SourceFilePath(
            root_path=Path("/root"), file_path=Path("/root/main.py")
        )
        assert str(source_file_path.module_path) == "main"

        code = SourceCode.build(
            file=SourceFile(
                source_file_path=source_file_path,
                size=100,
                content="from os import path, environ",
            )
        )

        assert code.build_import_dependency() == SourceCodeImportDependency(
            source_module_path=ModulePath.from_str("main"),
            import_paths=ImportPathCollection(
                [ImportPath.from_str("os.path"), ImportPath.from_str("os.environ")]
            ),
        )
