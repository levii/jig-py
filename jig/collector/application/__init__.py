import dataclasses
import os
from typing import List

from jig.collector.domain import SourceCode
from jig.collector.domain import SourceCodeCollectRequest
from jig.collector.domain import SourceFile


@dataclasses.dataclass(frozen=True)
class SourceCodeCollector:
    root_path: str

    def collect(self, target_path: str) -> SourceCode:
        # TODO: target_path が存在するかチェック

        source = open(target_path).read()

        return SourceCodeCollectRequest(
            root_path=self.root_path,
            file=SourceFile(
                path=target_path, content=source, size=os.path.getsize(target_path),
            ),
        ).build()

    def collect_directories(self) -> List[SourceCode]:
        result: List[SourceCode] = []
        for curDir, dirs, files in os.walk(os.path.join(self.root_path, 'jig')):
            for file in files:
                if not file.endswith('.py'):
                    continue
                file_path = os.path.join(curDir, file)
                result.append(self.collect(file_path))

        return result


def collect(root_path: str, target_path: str) -> SourceCode:
    collector = SourceCodeCollector(root_path=root_path)

    return collector.collect(target_path=target_path)
