import ast
import dataclasses
import os
import sys
from typing import List


# Domains
@dataclasses.dataclass(frozen=True)
class ModulePath:
    _path: str


@dataclasses.dataclass(frozen=True)
class ImportModule:
    module_path: ModulePath


@dataclasses.dataclass(frozen=True)
class SourceCodeAST:
    _ast: ast.Module

    @dataclasses.dataclass
    class ImportVisitor(ast.NodeVisitor):
        imports: List[ast.Import] = dataclasses.field(default_factory=list)

        def visit_Import(self, node):
            self.imports.append(node)

    def get_imports(self) -> List[ImportModule]:
        visitor = self.ImportVisitor()
        visitor.visit(self._ast)

        names = []
        for import_node in visitor.imports:
            for name_alias in import_node.names:
                names.append(name_alias.name)

        return [ImportModule(module_path=ModulePath(_path=name)) for name in names]


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


@dataclasses.dataclass(frozen=True)
class SourceCodeCollectRequest:
    file: SourceFile
    ast: SourceCodeAST

    def build(self) -> SourceCode:
        return SourceCode(
            file=self.file,
            ast=self.ast,
            import_modules= self._build_import_module_collection(),
        )

    def _build_import_module_collection(self):
        return ImportModuleCollection(self.ast.get_imports())


# Applications & Infrastructures

class SourceCodeCollector:
    def collect(self, target_path: str) -> SourceCode:
        # TODO: target_path が存在するかチェック

        source = open(target_path).read()
        tree = ast.parse(source=source, filename=os.path.basename(target_path))

        return SourceCodeCollectRequest(
            file=SourceFile(
                path=target_path,
                size=os.path.getsize(target_path),
            ),
            ast=SourceCodeAST(_ast=tree),
        ).build()


def collect(target_path: str) -> SourceCode:
    collector = SourceCodeCollector()

    return collector.collect(target_path=target_path)


if __name__ == "__main__":
    result = collect(target_path=sys.argv[1])
    print(result)
