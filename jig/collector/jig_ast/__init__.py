import dataclasses
from typed_ast import ast3 as ast
from typing import List

from jig.collector.jig_ast.class_def import ClassDef
from jig.collector.jig_ast.class_def import ClassDefVisitor
from jig.collector.jig_ast.imports import Import
from jig.collector.jig_ast.imports import ImportFrom
from jig.collector.jig_ast.imports import ImportFromVisitor
from jig.collector.jig_ast.imports import ImportVisitor


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
