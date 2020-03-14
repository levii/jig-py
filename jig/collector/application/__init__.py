import os

from jig.collector.domain import SourceCode
from jig.collector.domain import SourceCodeCollectRequest
from jig.collector.domain import SourceFile


class SourceCodeCollector:
    def collect(self, target_path: str) -> SourceCode:
        # TODO: target_path が存在するかチェック

        source = open(target_path).read()

        return SourceCodeCollectRequest(
            file=SourceFile(
                path=target_path,
                content=source,
                size=os.path.getsize(target_path),
            ),
        ).build()


def collect(target_path: str) -> SourceCode:
    collector = SourceCodeCollector()

    return collector.collect(target_path=target_path)
