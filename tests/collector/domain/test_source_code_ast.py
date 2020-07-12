from pathlib import Path

from jig.collector.domain.values.import_path import ImportPath
from jig.collector.domain.values.import_path_collection import ImportPathCollection
from jig.collector.domain.source_code.source_code import SourceCode
from jig.collector.domain.source_file.source_file import SourceFile
from jig.collector.domain.source_file.source_file_path import SourceFilePath


def collection(*args):
    modules = [ImportPath.from_str(p) for p in args]

    return ImportPathCollection(modules)


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

        assert ast.import_paths == collection("os", "datetime")

    def test_multiple_lines(self):
        content = """
import os
import datetime as dt
        """

        file = SourceFile(
            source_file_path=self.SOURCE_FILE_PATH, content=content, size=len(content),
        )
        ast = SourceCode.build(file)

        assert ast.import_paths == collection("os", "datetime")

    def test_import_from(self):
        content = """
from os import path
        """

        file = SourceFile(
            source_file_path=self.SOURCE_FILE_PATH, content=content, size=len(content),
        )
        ast = SourceCode.build(file)

        assert ast.import_paths == collection("os.path")

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
        assert ast.import_paths == collection(*modules)
