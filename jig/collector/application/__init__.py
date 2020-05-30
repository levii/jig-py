import dataclasses
import os
from typing import List

from jig.collector.domain import FilePath
from jig.collector.domain import SourceCode
from jig.collector.domain import SourceFile


@dataclasses.dataclass(frozen=True)
class SourceCodeCollector:
    root_path: str

    def collect(self, target_path: str) -> List[SourceCode]:
        file_path = FilePath(root_path=self.root_path, relative_path=target_path)

        source_codes = []
        if os.path.isdir(file_path.abspath):
            source_codes.extend(self.collect_directory(target_path))
        else:
            source_codes.append(self.collect_file(target_path))

        return source_codes

    def collect_file(self, target_path: str) -> SourceCode:
        source = open(target_path).read()

        return SourceCode.build(
            file=SourceFile(
                path=FilePath(root_path=self.root_path, relative_path=target_path),
                content=source,
                size=os.path.getsize(target_path),
            ),
        )

    def collect_directory(self, target_path: str) -> List[SourceCode]:
        file_path = FilePath(root_path=self.root_path, relative_path=target_path)

        result = []
        for cur_dir, dirs, files in os.walk(file_path.abspath):
            for file in files:
                if not file.endswith(".py"):
                    continue
                path = FilePath.build_with_abspath(
                    root_path=self.root_path, abspath=os.path.join(cur_dir, file)
                )
                result.append(self.collect_file(target_path=path.relative_path))

        return result
