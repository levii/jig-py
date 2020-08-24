from pathlib import Path

from jig.collector.domain.values.import_path import ImportPath
from jig.collector.domain.values.module_path import ModulePath
from jig.collector.domain.source_file.source_file_path import SourceFilePath
from tests.collector.domain.helper import parse_import_from


def mod(path: str) -> ModulePath:
    return ModulePath.from_str(path)


def import_path(path: str) -> ImportPath:
    return ImportPath.from_str(path)


class TestSourceFilePath:
    def test_filename(self):
        path = SourceFilePath(root_path=Path("root"), file_path=Path("root/main.py"))
        assert path.filename == "main.py"

    def test_module_path__level_1(self):
        path = SourceFilePath(root_path=Path("root"), file_path=Path("root/main.py"))

        assert not path.is_package
        assert path.module_path == ModulePath.from_str("main")

    def test_module_path__level_3(self):
        path = SourceFilePath(
            root_path=Path("root"), file_path=Path("root/path/to/file.py")
        )

        assert not path.is_package
        assert path.module_path == ModulePath.from_str("path.to.file")

    def test_module_path__init(self):
        path = SourceFilePath(
            root_path=Path("root"), file_path=Path("root/path/to/__init__.py")
        )

        assert path.is_package
        assert path.module_path == ModulePath.from_str("path.to")

    def test_can_convert_to_module_path__package(self):
        path = SourceFilePath(
            root_path=Path("root"), file_path=Path("root/path/to/__init__.py")
        )

        assert path.can_convert_to_module_path is True

    def test_can_convert_to_module_path__file(self):
        path = SourceFilePath(root_path=Path("root"), file_path=Path("root/main.py"))
        assert path.can_convert_to_module_path is True

    def test_can_convert_to_module_path__invalid_file(self):
        path = SourceFilePath(root_path=Path("root"), file_path=Path("root/.main.py"))
        assert path.can_convert_to_module_path is False

    def test_can_convert_to_module_path__invalid_path(self):
        path = SourceFilePath(
            root_path=Path("root"), file_path=Path("root/.hidden/main.py")
        )
        assert path.can_convert_to_module_path is False


class TestSourceFilePathResolveImportFrom:
    ROOT_PATH = Path("/jig-py")

    package_file_path = SourceFilePath(
        root_path=ROOT_PATH, file_path=Path("/jig-py/jig/collector/domain/__init__.py")
    )
    module_file_path = SourceFilePath(
        root_path=ROOT_PATH, file_path=Path("/jig-py/jig/collector/domain.py")
    )

    def test_module_path(self):
        assert self.package_file_path.module_path == mod("jig.collector.domain")
        assert self.package_file_path.module_path == self.module_file_path.module_path

    def test_builtin_module(self):
        import_from = parse_import_from("from os import path")

        assert self.package_file_path.import_from_to_import_paths(import_from) == [
            import_path("os.path")
        ]
        assert self.module_file_path.import_from_to_import_paths(import_from) == [
            import_path("os.path")
        ]

    def test_multiple_import_names(self):
        import_from = parse_import_from("from datetime import datetime, timezone")

        expected = [
            import_path("datetime.datetime"),
            import_path("datetime.timezone"),
        ]

        assert (
            self.package_file_path.import_from_to_import_paths(import_from) == expected
        )
        assert (
            self.module_file_path.import_from_to_import_paths(import_from) == expected
        )

    def test_nested_module(self):
        import_from = parse_import_from("from os.path import basename")

        assert self.package_file_path.import_from_to_import_paths(import_from) == [
            import_path("os.path.basename")
        ]

    def test_external_module(self):
        import_from = parse_import_from("from typed_ast import ast3 as ast")

        assert self.package_file_path.import_from_to_import_paths(import_from) == [
            import_path("typed_ast.ast3")
        ]
        assert self.module_file_path.import_from_to_import_paths(import_from) == [
            import_path("typed_ast.ast3")
        ]

    def test_import_from_current_path(self):
        import_from = parse_import_from("from . import sibling")

        assert self.package_file_path.import_from_to_import_paths(import_from) == [
            import_path("jig.collector.domain.sibling")
        ]
        assert self.module_file_path.import_from_to_import_paths(import_from) == [
            import_path("jig.collector.sibling")
        ]

    def test_import_from_current_path_with_module_name(self):
        import_from = parse_import_from("from .sibling import submodule")

        assert self.package_file_path.import_from_to_import_paths(import_from) == [
            import_path("jig.collector.domain.sibling.submodule")
        ]
        assert self.module_file_path.import_from_to_import_paths(import_from) == [
            import_path("jig.collector.sibling.submodule")
        ]

    def test_import_from_parent_path(self):
        import_from = parse_import_from("from .. import jig_ast")

        assert self.package_file_path.import_from_to_import_paths(import_from) == [
            import_path("jig.collector.jig_ast")
        ]
        assert self.module_file_path.import_from_to_import_paths(import_from) == [
            import_path("jig.jig_ast")
        ]

    def test_import_from_parent_path_with_module_name(self):
        import_from = parse_import_from("from ..jig_ast import submodule")

        assert self.package_file_path.import_from_to_import_paths(import_from) == [
            import_path("jig.collector.jig_ast.submodule")
        ]
        assert self.module_file_path.import_from_to_import_paths(import_from) == [
            import_path("jig.jig_ast.submodule")
        ]
