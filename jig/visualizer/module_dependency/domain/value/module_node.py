import dataclasses
from typing import Optional

from jig.visualizer.module_dependency.domain.value.node_style import NodeStyle
from .module_path import ModulePath


@dataclasses.dataclass(frozen=True)
class ModuleNode:
    path: ModulePath
    style: NodeStyle = dataclasses.field(default_factory=NodeStyle, compare=False)

    @classmethod
    def from_str(cls, path: str) -> "ModuleNode":
        return cls(path=ModulePath(name=path))

    @classmethod
    def build(cls, path: ModulePath, style: Optional[NodeStyle] = None) -> "ModuleNode":
        return cls(path=path, style=style or NodeStyle())

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def path_level(self) -> int:
        return self.path.path_level

    def path_in_depth(self, depth: int) -> ModulePath:
        return self.path.path_in_depth(depth)

    def __lt__(self, other: "ModuleNode"):
        return self.path < other.path

    def belongs_to(self, other: "ModuleNode") -> bool:
        return self.path.belongs_to(other.path)

    def limit_path_level(self, max_path_level: int) -> "ModuleNode":
        assert max_path_level > 0

        new_path = self.path.limit_path_level(max_path_level)
        return ModuleNode(new_path)

    def to_invisible(self) -> "ModuleNode":
        return self.build(path=self.path, style=NodeStyle(invisible=True))

    def with_style(self, style: NodeStyle) -> "ModuleNode":
        return self.build(path=self.path, style=style)

    def reset_style(self) -> "ModuleNode":
        return self.build(path=self.path)
