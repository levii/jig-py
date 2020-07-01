import dataclasses
import os
from pathlib import Path
from typing import List

from jig.collector.domain import (
    SourceCode,
    SourceCodeCollection,
    SourceFile,
    SourceFilePath,
)


@dataclasses.dataclass(frozen=True)
class SourceCodeCollector:
    root_path: Path

    def collect(self, target_path: Path) -> SourceCodeCollection:
        source_codes = []
        if target_path.is_dir():
            source_codes.extend(self.collect_directory(target_path))
        else:
            source_codes.append(self.collect_file(target_path))

        return SourceCodeCollection(source_codes)

    def collect_file(self, target_path: Path) -> SourceCode:
        source = target_path.read_text()

        return SourceCode.build(
            file=SourceFile(
                source_file_path=SourceFilePath(
                    root_path=self.root_path, file_path=target_path
                ),
                content=source,
                size=os.path.getsize(str(target_path)),
            ),
        )

    def collect_directory(self, target_path: Path) -> List[SourceCode]:
        result = []
        for cur_dir, dirs, files in os.walk(str(target_path)):
            for file in files:
                if not file.endswith(".py"):
                    continue

                path = Path(cur_dir).joinpath(file)

                result.append(self.collect_file(target_path=path))

        return result
