import dataclasses
from typed_ast import ast3 as ast
from typing import List, Optional


@dataclasses.dataclass(frozen=True)
class Alias:
    name: str
    asname: Optional[str]


@dataclasses.dataclass(frozen=True)
class Import:
    names: List[Alias]


@dataclasses.dataclass(frozen=True)
class ImportFrom:
    """
    module: fromで設定されるモジュール名。'from . import xxxx' の場合はNone
    names: importリスト
    level: fromのインポートレベル。'from os' => 0, 'from .' => 1, 'from ..' => 2
           levelがNoneになる条件は不明だが、ドキュメントの定義に合わせてOptional型で定義している
    """

    module: Optional[str]
    names: List[Alias]
    level: Optional[int]

    @classmethod
    def from_ast(cls, import_from: ast.ImportFrom) -> "ImportFrom":
        names = [
            Alias(name=alias.name, asname=alias.asname) for alias in import_from.names
        ]

        return cls(module=import_from.module, names=names, level=import_from.level)


@dataclasses.dataclass(frozen=True)
class JigAST:
    _ast: ast.AST

    @classmethod
    def parse(cls, source, filename: str = "<unknown>") -> "JigAST":
        tree = ast.parse(source=source, filename=filename)
        return cls(tree)

    @dataclasses.dataclass
    class ImportVisitor(ast.NodeVisitor):
        imports: List[ast.Import] = dataclasses.field(default_factory=list)
        import_froms: List[ast.ImportFrom] = dataclasses.field(default_factory=list)

        def visit_Import(self, node):
            self.imports.append(node)

        def visit_ImportFrom(self, node):
            self.import_froms.append(node)

    def imports(self) -> List[Import]:
        visitor = self.ImportVisitor()
        visitor.visit(self._ast)

        imports = []
        for import_node in visitor.imports:
            names = []
            for name_alias in import_node.names:
                names.append(Alias(name=name_alias.name, asname=name_alias.asname))
            imports.append(Import(names=names))

        return imports

    def import_froms(self) -> List[ImportFrom]:
        visitor = self.ImportVisitor()
        visitor.visit(self._ast)

        nodes = []
        for from_node in visitor.import_froms:
            names = [
                Alias(name=name_alias.name, asname=name_alias.asname)
                for name_alias in from_node.names
            ]

            nodes.append(
                ImportFrom(module=from_node.module, names=names, level=from_node.level)
            )

        return nodes
