from typing import List

from jig.analyzer.domain.dependency.import_dependency import ImportDependencyCollection
from jig.analyzer.domain.dependency.module_dependency import ModuleDependency
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

    def test_detect_module_path(self):
        collection = ImportDependencyCollection.build(
            dependencies=[
                build_dep(src_module_path="main", import_paths=["foo", "bar.BazClass"]),
                build_dep(src_module_path="foo", import_paths=[]),
                build_dep(src_module_path="bar", import_paths=[]),
            ]
        )

        assert (
            collection.detect_module_path(import_path=ImportPath.from_str("os.path"))
            is None
        )
        assert collection.detect_module_path(
            import_path=ImportPath.from_str("foo")
        ) == ModulePath.from_str("foo")
        assert collection.detect_module_path(
            import_path=ImportPath.from_str("bar.XXX")
        ) == ModulePath.from_str("bar")

    def test_build_module_dependencies(self):
        collection = ImportDependencyCollection.build(
            dependencies=[
                build_dep(
                    src_module_path="main",
                    import_paths=["foo", "bar.BazClass", "typing.List"],
                ),
                build_dep(src_module_path="foo", import_paths=["bar", "os.path"]),
                build_dep(src_module_path="bar", import_paths=[]),
            ]
        )

        dependencies = collection.build_module_dependencies()
        assert dependencies == [
            ModuleDependency.from_str("main", "foo"),
            ModuleDependency.from_str("main", "bar"),
            ModuleDependency.from_str("foo", "bar"),
        ]
