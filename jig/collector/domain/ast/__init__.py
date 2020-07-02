import dataclasses
from typing import Optional, List

from typed_ast import ast3 as ast


@dataclasses.dataclass(frozen=True)
class ClassDef:
    name: str
    _ast: ast.ClassDef = dataclasses.field(repr=False, compare=False)


@dataclasses.dataclass(frozen=True)
class Alias:
    name: str
    asname: Optional[str]


@dataclasses.dataclass(frozen=True)
class Import:
    names: List[Alias]
    _ast: ast.Import = dataclasses.field(repr=False, compare=False)

    @classmethod
    def from_ast(cls, import_ast: ast.Import) -> "Import":
        names = [
            Alias(name=name_alias.name, asname=name_alias.asname)
            for name_alias in import_ast.names
        ]

        return cls(names=names, _ast=import_ast)


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
    _ast: ast.ImportFrom = dataclasses.field(repr=False, compare=False)

    @classmethod
    def from_ast(cls, import_from: ast.ImportFrom) -> "ImportFrom":
        names = [
            Alias(name=alias.name, asname=alias.asname) for alias in import_from.names
        ]

        return cls(
            module=import_from.module,
            names=names,
            level=import_from.level,
            _ast=import_from,
        )


@dataclasses.dataclass(frozen=True)
class JigAST:
    _ast: ast.AST

    @classmethod
    def parse(cls, source: str, filename: str = "<unknown>") -> "JigAST":
        tree = ast.parse(source=source, filename=filename)
        return cls(tree)

    def imports(self) -> List[Import]:
        visitor = ImportVisitor()
        visitor.visit(self._ast)

        return visitor.imports

    def import_froms(self) -> List[ImportFrom]:
        visitor = ImportFromVisitor()
        visitor.visit(self._ast)

        return visitor.import_froms

    def class_defs(self) -> List[ClassDef]:
        visitor = ClassDefVisitor()
        visitor.visit(self._ast)

        return visitor.class_defs


@dataclasses.dataclass(frozen=True)
class JigSourceCode:
    imports: List[Import]
    import_froms: List[ImportFrom]
    class_defs: List[ClassDef]

    @classmethod
    def build(cls, source: str, filename: str) -> "JigSourceCode":
        jig_ast = JigAST.parse(source=source, filename=filename)

        return cls(
            imports=jig_ast.imports(),
            import_froms=jig_ast.import_froms(),
            class_defs=jig_ast.class_defs(),
        )


@dataclasses.dataclass
class ClassDefVisitor(ast.NodeVisitor):
    class_defs: List[ClassDef] = dataclasses.field(default_factory=list)

    def visit_ClassDef(self, node):
        self.class_defs.append(ClassDef(name=node.name, _ast=node,))


@dataclasses.dataclass
class ImportVisitor(ast.NodeVisitor):
    imports: List[Import] = dataclasses.field(default_factory=list)

    def visit_Import(self, node):
        self.imports.append(Import.from_ast(node))


@dataclasses.dataclass
class ImportFromVisitor(ast.NodeVisitor):
    import_froms: List[ImportFrom] = dataclasses.field(default_factory=list)

    def visit_ImportFrom(self, node):
        self.import_froms.append(
            ImportFrom(
                module=node.module,
                names=[
                    Alias(name=name_alias.name, asname=name_alias.asname)
                    for name_alias in node.names
                ],
                level=node.level,
                _ast=node,
            )
        )
