import dataclasses
from typing import List, Dict, Optional

from jig.collector.domain.source_code.source_code_collection import SourceCodeCollection
from jig.collector.domain.source_code.source_code_import_dependency import (
    SourceCodeImportDependency,
)
from jig.collector.domain.values.module_path import ModulePath


@dataclasses.dataclass(frozen=True)
class ImportDependencyCollection:
    _dependencies: Dict[str, SourceCodeImportDependency]

    @classmethod
    def build(
        cls, dependencies: List[SourceCodeImportDependency]
    ) -> "ImportDependencyCollection":
        return cls(
            _dependencies={
                str(dependency.source_module_path): dependency
                for dependency in dependencies
            }
        )

    @classmethod
    def build_from_source_code_collection(
        cls, source_code_collection: SourceCodeCollection
    ) -> "ImportDependencyCollection":
        return cls.build(
            dependencies=[
                source_code.build_import_dependency()
                for source_code in source_code_collection
            ]
        )

    def get_by_module_path(
        self, module_path: ModulePath
    ) -> Optional[SourceCodeImportDependency]:
        return self._dependencies.get(str(module_path))