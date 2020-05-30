import dataclasses
from typed_ast import ast3 as ast
from typing import List


@dataclasses.dataclass(frozen=True)
class ClassDef:
    name: str
    _ast: ast.ClassDef = dataclasses.field(repr=False, compare=False)


@dataclasses.dataclass
class ClassDefVisitor(ast.NodeVisitor):
    class_defs: List[ClassDef] = dataclasses.field(default_factory=list)

    def visit_ClassDef(self, node):
        self.class_defs.append(ClassDef(name=node.name, _ast=node,))
