import dataclasses
from typing import Union, List

from jig.collector.domain.values.import_path import ImportPath
from jig.collector.domain.values.import_path_collection import ImportPathCollection
from jig.collector.domain.values.module_path import ModulePath


@dataclasses.dataclass(frozen=True)
class SourceCodeImportDependency:
    source_module_path: ModulePath
    import_paths: ImportPathCollection

    @classmethod
    def build(
        cls,
        source_module_path: ModulePath,
        import_paths: Union[List[ImportPath], ImportPathCollection],
    ) -> "SourceCodeImportDependency":
        if not isinstance(import_paths, ImportPathCollection):
            import_paths = ImportPathCollection(import_paths)

        return cls(source_module_path=source_module_path, import_paths=import_paths)
