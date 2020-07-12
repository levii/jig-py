import dataclasses

from jig.collector.domain.values.module_path import ModulePath
from jig.collector.domain.source_file.source_file_path import SourceFilePath


@dataclasses.dataclass(frozen=True)
class SourceFile:
    source_file_path: SourceFilePath
    size: int
    content: str = dataclasses.field(repr=False)

    @property
    def filename(self):
        return self.source_file_path.filename

    @property
    def module_path(self) -> ModulePath:
        return self.source_file_path.module_path
