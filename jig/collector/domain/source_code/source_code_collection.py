import dataclasses
from typing import List, Optional

from jig.collector.domain.source_code.source_code import SourceCode


@dataclasses.dataclass(frozen=True)
class SourceCodeCollection:
    collection: List[SourceCode]

    def __iter__(self):
        return self.collection.__iter__()

    def __len__(self):
        return self.collection.__len__()

    def __getitem__(self, item):
        return self.collection.__getitem__(item)

    def get_by_relative_path(self, relative_path: str) -> Optional[SourceCode]:
        for source_code in self.collection:
            source_file_path = source_code.file.source_file_path
            if str(source_file_path.relative_path_from_root) == relative_path:
                return source_code
        return None
