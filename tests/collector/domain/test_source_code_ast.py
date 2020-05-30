from jig.collector.domain import FilePath
from jig.collector.domain import SourceCode
from jig.collector.domain import (
    SourceFile,
    ModulePath,
    ImportModule,
    ImportModuleCollection,
)


def collection(*args):
    modules = [ImportModule(ModulePath(p)) for p in args]

    return ImportModuleCollection(modules)


class TestSourceCodeASTGetImports:
    ROOT_PATH = "/jig-py"
    SOURCE_PATH = "/jig-py/jig/collector/domain/__init__.py"
    FILE_PATH = FilePath.build_with_abspath(root_path=ROOT_PATH, abspath=SOURCE_PATH)

    def test_multiple_modules(self):
        content = """
import os, datetime
        """

        file = SourceFile(path=self.FILE_PATH, content=content, size=len(content))
        ast = SourceCode.build(file)

        assert ast.import_modules == collection("os", "datetime")

    def test_multiple_lines(self):
        content = """
import os
import datetime as dt
        """

        file = SourceFile(path=self.FILE_PATH, content=content, size=len(content))
        ast = SourceCode.build(file)

        assert ast.import_modules == collection("os", "datetime")

    def test_import_from(self):
        content = """
from os import path
        """

        file = SourceFile(path=self.FILE_PATH, content=content, size=len(content))
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

        file = SourceFile(path=self.FILE_PATH, content=content, size=len(content))
        ast = SourceCode.build(file)

        modules = [
            "os",
            "datetime",
            "os.path",
            "jig.collector.domain.submodule",
            "jig.collector.jig_ast",
        ]
        assert ast.import_modules == collection(*modules)
