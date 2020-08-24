import dataclasses
import os
from pathlib import Path
from typing import List, Optional

from jig.collector.domain.source_code.source_code_collection import SourceCodeCollection
from jig.collector.domain.source_code.source_code import SourceCode
from jig.collector.domain.source_file.source_file import SourceFile
from jig.collector.domain.source_file.source_file_path import SourceFilePath


@dataclasses.dataclass(frozen=True)
class SourceCodeCollector:
    root_path: Path

    def collect(self, target_path: Path) -> SourceCodeCollection:
        source_codes = []
        if target_path.is_dir():
            source_codes.extend(self.collect_directory(target_path))
        else:
            source_code = self.collect_file(target_path)
            if source_code:
                source_codes.append(source_code)

        return SourceCodeCollection(source_codes)

    def collect_file(self, target_path: Path) -> Optional[SourceCode]:
        source_file_path = SourceFilePath(
            root_path=self.root_path, file_path=target_path
        )
        if not source_file_path.can_convert_to_module_path:
            return None

        source = target_path.read_text()

        return SourceCode.build(
            file=SourceFile(
                source_file_path=source_file_path,
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

                source_code = self.collect_file(target_path=path)
                if source_code:
                    result.append(source_code)

        return result
