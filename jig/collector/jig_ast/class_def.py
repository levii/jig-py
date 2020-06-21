import dataclasses
from typed_ast import ast3 as ast
from typing import List

from jig.collector.domain.ast import ClassDef


@dataclasses.dataclass
class ClassDefVisitor(ast.NodeVisitor):
    class_defs: List[ClassDef] = dataclasses.field(default_factory=list)

    def visit_ClassDef(self, node):
        self.class_defs.append(ClassDef(name=node.name, _ast=node,))
