import ast
import dataclasses
from typing import List, Optional


@dataclasses.dataclass(frozen=True)
class Import:
    names: List[ast.alias]


class Alias:
    name: str
    asname: Optional[str]


@dataclasses.dataclass(frozen=True)
class AST:
    _ast: ast.Module

    @dataclasses.dataclass
    class ImportVisitor(ast.NodeVisitor):
        imports: List[ast.Import] = dataclasses.field(default_factory=list)

        def visit_Import(self, node):
            self.imports.append(node)

    def get_imports(self) -> List[ast.Import]:
        visitor = self.ImportVisitor()
        visitor.visit(self._ast)

        return visitor.imports

