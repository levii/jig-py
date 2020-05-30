import dataclasses
import os

from jig.collector.domain import FilePath
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
                path=FilePath(root_path=self.root_path, relative_path=target_path),
                content=source,
                size=os.path.getsize(target_path),
            ),
        ).build()


def collect(root_path: str, target_path: str) -> SourceCode:
    collector = SourceCodeCollector(root_path=root_path)

    return collector.collect(target_path=target_path)
