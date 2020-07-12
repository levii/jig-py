from pathlib import Path

from jig.collector.domain import SourceFilePath, ModulePath
from jig.collector.domain import ImportModule, ImportPathCollection
from .helper import parse_import_from, parse_import


def mod_collections(*modules) -> ImportPathCollection:
    return ImportPathCollection(
        [ImportModule(module_path=ModulePath.from_str(module)) for module in modules]
    )


class TestImportModuleCollectionBuildByImportFromAST:
    ROOT_PATH = "/jig-py"
    CURRENT_PATH = "/jig-py/jig/collector/domain/__init__.py"
    SOURCE_FILE_PATH = SourceFilePath(
        root_path=Path(ROOT_PATH), file_path=Path(CURRENT_PATH)
    )

    def test_builtin_module(self):
        import_from = parse_import_from("from os import path")

        import_modules = ImportPathCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert import_modules == mod_collections("os.path")

    def test_multiple_import_module(self):
        import_from = parse_import_from("from datetime import datetime, timezone")

        import_modules = ImportPathCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert import_modules == mod_collections(
            "datetime.datetime", "datetime.timezone"
        )

    def test_external_module(self):
        import_from = parse_import_from("from typed_ast import ast3 as ast")

        import_modules = ImportPathCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert import_modules == mod_collections("typed_ast.ast3")

    def test_import_from_current_path(self):
        import_from = parse_import_from("from . import sibling")

        import_modules = ImportPathCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert import_modules == mod_collections("jig.collector.domain.sibling")

    def test_import_from_current_path_with_module_name(self):
        import_from = parse_import_from("from .sibling import submodule")

        import_modules = ImportPathCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert import_modules == mod_collections(
            "jig.collector.domain.sibling.submodule"
        )

    def test_import_from_parent_path(self):
        import_from = parse_import_from("from .. import jig_ast")

        import_modules = ImportPathCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert len(import_modules) == 1
        assert (
            ImportModule(ModulePath.from_str("jig.collector.jig_ast")) in import_modules
        )

    def test_import_from_parent_path_with_module_name(self):
        import_from = parse_import_from("from ..jig_ast import submodule")

        import_modules = ImportPathCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert import_modules == mod_collections("jig.collector.jig_ast.submodule")

    def test_import_from_nested_module(self):
        import_from = parse_import_from("from .aaa.bbb import xxx")

        import_modules = ImportPathCollection.build_by_import_from_ast(
            file_path=self.SOURCE_FILE_PATH, import_from=import_from
        )

        assert import_modules == mod_collections("jig.collector.domain.aaa.bbb.xxx")


class TestImportModuleCollectionBuildByImportAST:
    def test_one_module(self):
        import_ast = parse_import("import os")

        import_modules = ImportPathCollection.build_by_import_ast(import_ast)
        assert import_modules == mod_collections("os")

    def test_nested_module(self):
        import_ast = parse_import("import datetime.datetime")

        import_modules = ImportPathCollection.build_by_import_ast(import_ast)
        assert import_modules == mod_collections("datetime.datetime")

    def test_multiple_modules(self):
        import_ast = parse_import("import os, datetime.datetime")

        import_modules = ImportPathCollection.build_by_import_ast(import_ast)
        assert import_modules == mod_collections("os", "datetime.datetime")

    def test_to_module_path_list(self):
        import_ast = parse_import("import os, datetime.datetime")

        import_modules = ImportPathCollection.build_by_import_ast(import_ast)
        assert import_modules.to_module_path_list() == [
            ModulePath.from_str("os"),
            ModulePath.from_str("datetime.datetime"),
        ]
