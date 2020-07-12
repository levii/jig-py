import dataclasses

from jig.collector.domain.values.import_path_collection import ImportPathCollection
from jig.collector.domain.values.module_path import ModulePath


@dataclasses.dataclass(frozen=True)
class SourceCodeImportDependency:
    source_module_path: ModulePath
    import_paths: ImportPathCollection

    @classmethod
    def build(
        cls, source_module_path: ModulePath, import_paths: ImportPathCollection
    ) -> "SourceCodeImportDependency":
        return cls(source_module_path=source_module_path, import_paths=import_paths)
