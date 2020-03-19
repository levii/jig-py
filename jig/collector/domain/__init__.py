import dataclasses
import os
from typing import List

from jig.collector.jig_ast import JigAST


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
        return cls(_ast=JigAST.parse(source=source.content, filename=source.filename))

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
        return SourceCode(file=self.file, ast=ast, import_modules=ast.get_imports(),)
