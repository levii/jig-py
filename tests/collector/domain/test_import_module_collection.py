from pathlib import Path

from jig.collector.domain import SourceFilePath, ModulePath
from jig.collector.domain import ImportModule, ImportModuleCollection
from .helper import parse_import_from


class TestImportModuleCollectionBuildByImportFromAST:
    ROOT_PATH = "/jig-py"
    CURRENT_PATH = "/jig-py/jig/collector/domain/__init__.py"
    SOURCE_FILE_PATH = SourceFilePath(
        root_path=Path(ROOT_PATH), file_path=Path(CURRENT_PATH)
    )

    def test_builtin_module(self):
        import_from = parse_import_from("from os import path")

        import_modules = ImportModuleCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert len(import_modules) == 1
        assert ImportModule(ModulePath.from_str("os.path")) in import_modules

    def test_multiple_import_module(self):
        import_from = parse_import_from("from datetime import datetime, timezone")

        import_modules = ImportModuleCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert len(import_modules) == 2
        assert ImportModule(ModulePath.from_str("datetime.datetime")) in import_modules
        assert ImportModule(ModulePath.from_str("datetime.timezone")) in import_modules

    def test_external_module(self):
        import_from = parse_import_from("from typed_ast import ast3 as ast")

        import_modules = ImportModuleCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert len(import_modules) == 1
        assert ImportModule(ModulePath.from_str("typed_ast.ast3")) in import_modules

    def test_import_from_current_path(self):
        import_from = parse_import_from("from . import sibling")

        import_modules = ImportModuleCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert len(import_modules) == 1
        assert (
            ImportModule(ModulePath.from_str("jig.collector.domain.sibling"))
            in import_modules
        )

    def test_import_from_current_path_with_module_name(self):
        import_from = parse_import_from("from .sibling import submodule")

        import_modules = ImportModuleCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert len(import_modules) == 1
        assert (
            ImportModule(ModulePath.from_str("jig.collector.domain.sibling.submodule"))
            in import_modules
        )

    def test_import_from_parent_path(self):
        import_from = parse_import_from("from .. import jig_ast")

        import_modules = ImportModuleCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert len(import_modules) == 1
        assert (
            ImportModule(ModulePath.from_str("jig.collector.jig_ast")) in import_modules
        )

    def test_import_from_parent_path_with_module_name(self):
        import_from = parse_import_from("from ..jig_ast import submodule")

        import_modules = ImportModuleCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert len(import_modules) == 1
        assert (
            ImportModule(ModulePath.from_str("jig.collector.jig_ast.submodule"))
            in import_modules
        )

    def test_import_from_nested_module(self):
        import_from = parse_import_from("from .aaa.bbb import xxx")

        import_modules = ImportModuleCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert len(import_modules) == 1
        assert (
            ImportModule(ModulePath.from_str("jig.collector.domain.aaa.bbb.xxx"))
            in import_modules
        )
