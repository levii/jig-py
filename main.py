import dataclasses
import os
import sys
from typing import List


# Domains
from collector.jig_ast import JigAST


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
    content: str
    size: int

    @property
    def filename(self):
        return os.path.basename(self.path)


@dataclasses.dataclass(frozen=True)
class SourceCodeAST:
    _ast: JigAST

    @classmethod
    def build(cls, source: SourceFile):
        return cls(
            _ast=JigAST.parse(source=source.content, filename=source.filename)
        )

    def get_imports(self) -> ImportModuleCollection:
        imports = []
        for import_node in self._ast.imports():
            for name in import_node.names:
                imports.append(ImportModule(module_path=ModulePath(_path=name.name)))

        return ImportModuleCollection(imports)


@dataclasses.dataclass(frozen=True)
class SourceCode:
    file: SourceFile
    ast: SourceCodeAST
    import_modules: ImportModuleCollection


@dataclasses.dataclass(frozen=True)
class SourceCodeCollectRequest:
    file: SourceFile

    def build(self) -> SourceCode:
        ast = SourceCodeAST.build(self.file)
        return SourceCode(
            file=self.file,
            ast=ast,
            import_modules=ast.get_imports(),
        )


# Applications & Infrastructures

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


if __name__ == "__main__":
    result = collect(target_path=sys.argv[1])
    print(result)
