import dataclasses
from typing import List

from jig.collector.domain.ast import ClassDef, JigSourceCode
from jig.collector.domain.source_code.source_code_import_dependency import (
    SourceCodeImportDependency,
)
from jig.collector.domain.values.import_path_collection import ImportPathCollection
from jig.collector.domain.values.module_dependency import ModuleDependency
from jig.collector.domain.values.module_path import ModulePath
from jig.collector.domain.source_file.source_file import SourceFile


@dataclasses.dataclass(frozen=True)
class SourceCode:
    file: SourceFile
    import_paths: ImportPathCollection
    class_defs: List[ClassDef]

    @property
    def module_path(self) -> ModulePath:
        return self.file.module_path

    @classmethod
    def build(cls, file: SourceFile) -> "SourceCode":
        jig_source_code = JigSourceCode.build(
            source=file.content, filename=file.filename
        )

        return SourceCode(
            file=file,
            import_paths=cls._build_import_paths(file, jig_source_code),
            class_defs=jig_source_code.class_defs,
        )

    def module_dependencies(
        self, module_names: List[str] = None
    ) -> List[ModuleDependency]:
        if not module_names:
            return [
                ModuleDependency(
                    src=self.module_path, dest=ModulePath.from_str(str(import_path)),
                )
                for import_path in self.import_paths
            ]

        dependencies = []
        for import_path in self.import_paths:
            if import_path.match_module_names(module_names):
                dependencies.append(
                    ModuleDependency(
                        src=self.module_path,
                        dest=ModulePath.from_str(str(import_path)),
                    )
                )

        return dependencies

    @classmethod
    def _build_import_paths(
        cls, file: SourceFile, jig_source_code: JigSourceCode
    ) -> ImportPathCollection:
        import_paths = ImportPathCollection()

        for import_ast in jig_source_code.imports:
            import_paths += ImportPathCollection.build_by_import_ast(import_ast)

        for import_from_ast in jig_source_code.import_froms:
            import_paths += ImportPathCollection.build_by_import_from_ast(
                file_path=file.source_file_path, import_from=import_from_ast
            )

        return import_paths

    def build_import_dependency(self) -> SourceCodeImportDependency:
        return SourceCodeImportDependency.build(
            source_module_path=self.file.module_path, import_paths=self.import_paths
        )
