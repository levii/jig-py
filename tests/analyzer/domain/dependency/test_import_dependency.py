from typing import List

from jig.analyzer.domain.dependency.import_dependency import ImportDependencyCollection
from jig.collector.domain.source_code.source_code_import_dependency import (
    SourceCodeImportDependency,
)
from jig.collector.domain.values.import_path import ImportPath
from jig.collector.domain.values.module_path import ModulePath


def build_dep(
    src_module_path: str, import_paths: List[str]
) -> SourceCodeImportDependency:
    return SourceCodeImportDependency.build(
        source_module_path=ModulePath.from_str(src_module_path),
        import_paths=[ImportPath.from_str(dest) for dest in import_paths],
    )


class TestImportDependencyCollection:
    def test_build(self):
        collection = ImportDependencyCollection.build(
            dependencies=[
                build_dep(
                    src_module_path="main", import_paths=["os.path", "typing.List"]
                )
            ]
        )
        assert isinstance(
            collection.get_by_module_path(ModulePath.from_str("main")),
            SourceCodeImportDependency,
        )
