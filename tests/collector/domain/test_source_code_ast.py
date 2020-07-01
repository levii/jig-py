from pathlib import Path

from jig.collector.domain import (
    SourceFile,
    SourceFilePath,
    ModulePath,
    ImportModule,
    ImportModuleCollection,
    SourceCode,
)


def collection(*args):
    modules = [ImportModule(ModulePath.from_str(p)) for p in args]

    return ImportModuleCollection(modules)


class TestSourceCodeASTGetImports:
    ROOT_PATH = "/jig-py"
    SOURCE_PATH = "/jig-py/jig/collector/domain/__init__.py"
    SOURCE_FILE_PATH = SourceFilePath(
        root_path=Path(ROOT_PATH), file_path=Path(SOURCE_PATH)
    )

    def test_multiple_modules(self):
        content = """
import os, datetime
        """

        file = SourceFile(
            source_file_path=self.SOURCE_FILE_PATH, content=content, size=len(content),
        )
        ast = SourceCode.build(file)

        assert ast.import_modules == collection("os", "datetime")

    def test_multiple_lines(self):
        content = """
import os
import datetime as dt
        """

        file = SourceFile(
            source_file_path=self.SOURCE_FILE_PATH, content=content, size=len(content),
        )
        ast = SourceCode.build(file)

        assert ast.import_modules == collection("os", "datetime")

    def test_import_from(self):
        content = """
from os import path
        """

        file = SourceFile(
            source_file_path=self.SOURCE_FILE_PATH, content=content, size=len(content),
        )
        ast = SourceCode.build(file)

        assert ast.import_modules == collection("os.path")

    def test_mixed_import(self):
        content = """
import os
import datetime as dt
from os import path
from . import submodule
from .. import jig_ast
        """

        file = SourceFile(
            source_file_path=self.SOURCE_FILE_PATH, content=content, size=len(content),
        )
        ast = SourceCode.build(file)

        modules = [
            "os",
            "datetime",
            "os.path",
            "jig.collector.domain.submodule",
            "jig.collector.jig_ast",
        ]
        assert ast.import_modules == collection(*modules)
