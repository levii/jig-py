import dataclasses
from typing import List

from jig.collector.domain.ast import ImportFrom, Import
from jig.collector.domain.values.import_path import ImportPath
from jig.collector.domain.source_file.source_file_path import SourceFilePath


@dataclasses.dataclass(frozen=True)
class ImportPathCollection:
    _paths: List[ImportPath] = dataclasses.field(default_factory=list)

    def __len__(self) -> int:
        return len(self._paths)

    def __contains__(self, item: ImportPath):
        return item in self._paths

    def __add__(self, other: "ImportPathCollection") -> "ImportPathCollection":
        return ImportPathCollection(self._paths + other._paths)

    def __iter__(self):
        return self._paths.__iter__()

    @classmethod
    def build_by_import_ast(cls, import_ast: Import) -> "ImportPathCollection":
        imports = [ImportPath.from_str(name.name) for name in import_ast.names]

        return ImportPathCollection(imports)

    @classmethod
    def build_by_import_from_ast(
        cls, file_path: SourceFilePath, import_from: ImportFrom
    ) -> "ImportPathCollection":

        imports = file_path.import_from_to_import_paths(import_from)
        return cls(_paths=imports)
