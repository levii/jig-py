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
class JigAST:
    _ast: ast.Module

    @classmethod
    def parse(cls, source, filename: str = "<unknown>") -> "JigAST":
        tree = ast.parse(source=source, filename=filename)
        return cls(tree)

    @dataclasses.dataclass
    class ImportVisitor(ast.NodeVisitor):
        imports: List[ast.Import] = dataclasses.field(default_factory=list)

        def visit_Import(self, node):
            self.imports.append(node)

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
