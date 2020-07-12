import dataclasses
from typing import List, Dict, Optional

from jig.analyzer.domain.dependency.module_dependency import ModuleDependency
from jig.collector.domain.source_code.source_code_collection import SourceCodeCollection
from jig.collector.domain.source_code.source_code_import_dependency import (
    SourceCodeImportDependency,
)
from jig.collector.domain.values.import_path import ImportPath
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

    def build_module_dependencies(self) -> List[ModuleDependency]:
        """
        selfで保持しているModulePathからImportPathへの依存情報を
        ModulePathからModulePathへの依存情報に変換する
        """
        dependencies = []
        for dep in self._dependencies.values():
            src = dep.source_module_path
            for dest_import_path in dep.import_paths:
                dest_module_path = self.detect_module_path(import_path=dest_import_path)
                if dest_module_path:
                    dependencies.append(
                        ModuleDependency(src=src, dest=dest_module_path)
                    )

        return dependencies

    def detect_module_path(self, import_path: ImportPath) -> Optional[ModulePath]:
        module_path = ModulePath.from_str(str(import_path))
        if self.get_by_module_path(module_path):
            return module_path

        if module_path.depth > 1:
            parent_path = module_path.parent()
            if self.get_by_module_path(parent_path):
                return parent_path

        return None
