import os
import urllib.request
import zipfile
import io
from pathlib import Path
from typing import Optional

from jig.collector.application import SourceCodeCollector
from jig.collector.domain import (
    ModulePath,
    ImportPathCollection,
    ImportPath,
)


class TestJigPy20200609:
    DOWNLOAD_PATH = os.path.join(
        os.environ["PYTEST_FIXTURES_PATH"], "download", "TestJigPy20200609"
    )
    ZIP_URL = "https://github.com/levii/jig-py/archive/e6871f13cf555b4bf1cf21b3398081b86699a8d2.zip"

    @classmethod
    def download_and_setup(cls) -> Optional[str]:
        detect_path = cls.get_code_path()
        if detect_path:
            return detect_path

        content = urllib.request.urlopen(cls.ZIP_URL).read()
        f = io.BytesIO()
        f.write(content)
        f.seek(0)

        with zipfile.ZipFile(f) as zip_f:
            zip_f.extractall(path=cls.DOWNLOAD_PATH)

        return cls.get_code_path()

    @classmethod
    def get_code_path(cls) -> Optional[str]:
        if not os.path.exists(cls.DOWNLOAD_PATH):
            return None

        directories = os.listdir(path=cls.DOWNLOAD_PATH)
        if len(directories) == 1:
            return os.path.join(cls.DOWNLOAD_PATH, directories[0])

        return None

    @classmethod
    def setup_class(cls):
        cls.download_and_setup()
        assert cls.get_code_path() is not None

    def test_collector(self):
        os.chdir(self.get_code_path())
        source_code_collection = SourceCodeCollector(
            root_path=Path(self.get_code_path())
        ).collect(Path("jig"))
        assert len(source_code_collection) == 10
        filenames = sorted(
            [
                str(code.file.source_file_path.relative_path_from_root)
                for code in source_code_collection
            ]
        )
        assert filenames == [
            "jig/__init__.py",
            "jig/collector/__init__.py",
            "jig/collector/application/__init__.py",
            "jig/collector/domain/__init__.py",
            "jig/collector/jig_ast/__init__.py",
            "jig/collector/jig_ast/class_def.py",
            "jig/collector/jig_ast/imports.py",
            "jig/visualizer/__init__.py",
            "jig/visualizer/application/__init__.py",
            "jig/visualizer/domain/__init__.py",
        ]

        jig_init_py = source_code_collection.get_by_relative_path("jig/__init__.py")
        assert jig_init_py.file.content == ""
        assert jig_init_py.module_path == ModulePath.from_str("jig")
        assert jig_init_py.import_paths == ImportPathCollection([])
        assert jig_init_py.class_defs == []

        jig_collector_jig_ast_init = source_code_collection.get_by_relative_path(
            "jig/collector/jig_ast/__init__.py"
        )
        assert jig_collector_jig_ast_init.module_path == ModulePath.from_str(
            "jig.collector.jig_ast"
        )
        assert jig_collector_jig_ast_init.import_paths == ImportPathCollection(
            [
                ImportPath.from_str("dataclasses"),
                ImportPath.from_str("typed_ast.ast3"),
                ImportPath.from_str("typing.List"),
                ImportPath.from_str("jig.collector.jig_ast.class_def.ClassDef"),
                ImportPath.from_str("jig.collector.jig_ast.class_def.ClassDefVisitor"),
                ImportPath.from_str("jig.collector.jig_ast.imports.Import"),
                ImportPath.from_str("jig.collector.jig_ast.imports.ImportFrom"),
                ImportPath.from_str("jig.collector.jig_ast.imports.ImportFromVisitor"),
                ImportPath.from_str("jig.collector.jig_ast.imports.ImportVisitor"),
            ]
        )

        jig_collector_application = source_code_collection.get_by_relative_path(
            "jig/collector/application/__init__.py"
        )
        assert jig_collector_application.module_path == ModulePath.from_str(
            "jig.collector.application"
        )
        assert jig_collector_application.import_paths == ImportPathCollection(
            [
                ImportPath.from_str("dataclasses"),
                ImportPath.from_str("os"),
                ImportPath.from_str("typing.List"),
                ImportPath.from_str("jig.collector.domain.FilePath"),
                ImportPath.from_str("jig.collector.domain.SourceCode"),
                ImportPath.from_str("jig.collector.domain.SourceFile"),
            ]
        )
