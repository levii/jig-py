import dataclasses
import os
import sys
from typing import List


# Domains

@dataclasses.dataclass(frozen=True)
class SourceCodeAST:
    pass


@dataclasses.dataclass(frozen=True)
class ModulePath:
    _path: str


@dataclasses.dataclass(frozen=True)
class ImportModule:
    module_path: ModulePath


@dataclasses.dataclass(frozen=True)
class ImportModuleCollection:
    _modules: List[ImportModule]


@dataclasses.dataclass(frozen=True)
class SourceFile:
    path: str
    size: int


@dataclasses.dataclass(frozen=True)
class SourceCode:
    file: SourceFile
    ast: SourceCodeAST
    import_modules: ImportModuleCollection


# Applications & Infrastructures

class SourceCodeCollector:
    def collect(self, target_path: str) -> SourceCode:
        # TODO: target_path が存在するかチェック

        return SourceCode(
            file=SourceFile(
                path=target_path,
                size=os.path.getsize(target_path),
            ),
            ast=SourceCodeAST(),
            import_modules=ImportModuleCollection([])
        )


def collect(target_path: str) -> SourceCode:
    collector = SourceCodeCollector()

    return collector.collect(target_path=target_path)


if __name__ == "__main__":
    result = collect(target_path=sys.argv[1])
    print(result)
