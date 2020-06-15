import os
import urllib.request
import zipfile
import io
from typing import Optional

from jig.collector.application import SourceCodeCollector
from jig.collector.domain import (
    ModulePath,
    ImportModuleCollection,
    ImportModule,
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
            root_path=self.get_code_path()
        ).collect("jig")
        assert len(source_code_collection) == 10
        filenames = sorted(
            [code.file.path.relative_path for code in source_code_collection]
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
        assert jig_init_py.module_path == ModulePath("jig")
        assert jig_init_py.import_modules == ImportModuleCollection([])
        assert jig_init_py.class_defs == []

        jig_collector_jig_ast_init = source_code_collection.get_by_relative_path(
            "jig/collector/jig_ast/__init__.py"
        )
        assert jig_collector_jig_ast_init.module_path == ModulePath(
            "jig.collector.jig_ast"
        )
        assert jig_collector_jig_ast_init.import_modules == ImportModuleCollection(
            [
                ImportModule(ModulePath("dataclasses")),
                ImportModule(ModulePath("typed_ast.ast3")),
                ImportModule(ModulePath("typing.List")),
                ImportModule(ModulePath("jig.collector.jig_ast.class_def.ClassDef")),
                ImportModule(
                    ModulePath("jig.collector.jig_ast.class_def.ClassDefVisitor")
                ),
                ImportModule(ModulePath("jig.collector.jig_ast.imports.Import")),
                ImportModule(ModulePath("jig.collector.jig_ast.imports.ImportFrom")),
                ImportModule(
                    ModulePath("jig.collector.jig_ast.imports.ImportFromVisitor")
                ),
                ImportModule(ModulePath("jig.collector.jig_ast.imports.ImportVisitor")),
            ]
        )

        jig_collector_application = source_code_collection.get_by_relative_path(
            "jig/collector/application/__init__.py"
        )
        assert jig_collector_application.module_path == ModulePath(
            "jig.collector.application"
        )
        assert jig_collector_application.import_modules == ImportModuleCollection(
            [
                ImportModule(ModulePath("dataclasses")),
                ImportModule(ModulePath("os")),
                ImportModule(ModulePath("typing.List")),
                ImportModule(ModulePath("jig.collector.domain.FilePath")),
                ImportModule(ModulePath("jig.collector.domain.SourceCode")),
                ImportModule(ModulePath("jig.collector.domain.SourceFile")),
            ]
        )
