from jig.analyzer.domain.dependency.import_dependency import ImportDependencyCollection
from jig.collector.domain.source_code.source_code_import_dependency import (
    SourceCodeImportDependency,
)
from jig.collector.domain.values.import_path import ImportPath
from jig.collector.domain.values.module_path import ModulePath


class TestImportDependencyCollection:
    def test_build(self):
        collection = ImportDependencyCollection.build(
            dependencies=[
                SourceCodeImportDependency.build(
                    source_module_path=ModulePath.from_str("main"),
                    import_paths=[
                        ImportPath.from_str("os.path"),
                        ImportPath.from_str("typing.List"),
                    ],
                )
            ]
        )
        assert isinstance(
            collection.get_by_module_path(ModulePath.from_str("main")),
            SourceCodeImportDependency,
        )
