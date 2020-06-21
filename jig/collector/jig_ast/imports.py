import dataclasses
from typed_ast import ast3 as ast
from typing import List

from jig.collector.domain.ast import Alias, Import, ImportFrom


@dataclasses.dataclass
class ImportVisitor(ast.NodeVisitor):
    imports: List[Import] = dataclasses.field(default_factory=list)

    def visit_Import(self, node):
        self.imports.append(
            Import(
                names=[
                    Alias(name=name_alias.name, asname=name_alias.asname)
                    for name_alias in node.names
                ],
                _ast=node,
            )
        )


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
