from jig.collector.domain import FilePath
from jig.collector.domain import (
    SourceCodeAST,
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

        source = SourceFile(path=self.FILE_PATH, content=content, size=len(content))
        ast = SourceCodeAST.build(root_path=self.ROOT_PATH, source=source)

        assert ast.get_imports() == collection("os", "datetime")

    def test_multiple_lines(self):
        content = """
import os
import datetime as dt
        """

        source = SourceFile(path=self.FILE_PATH, content=content, size=len(content))
        ast = SourceCodeAST.build(root_path=self.ROOT_PATH, source=source)

        assert ast.get_imports() == collection("os", "datetime")

    def test_import_from(self):
        content = """
from os import path
        """

        source = SourceFile(path=self.FILE_PATH, content=content, size=len(content))
        ast = SourceCodeAST.build(root_path=self.ROOT_PATH, source=source)

        assert ast.get_imports() == collection("os.path")

    def test_mixed_import(self):
        content = """
import os
import datetime as dt
from os import path
from . import submodule
from .. import jig_ast
        """

        source = SourceFile(path=self.FILE_PATH, content=content, size=len(content))
        ast = SourceCodeAST.build(root_path=self.ROOT_PATH, source=source)

        modules = [
            "os",
            "datetime",
            "os.path",
            "jig.collector.domain.submodule",
            "jig.collector.jig_ast",
        ]
        assert ast.get_imports() == collection(*modules)
