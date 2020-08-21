import dataclasses
from typing import Dict, Optional

from .color import Color
from .module_path import ModulePath


@dataclasses.dataclass(frozen=True)
class ModuleNodeStyle:
    color: Color = dataclasses.field(default=Color.Black)
    fontcolor: Color = dataclasses.field(default=Color.Black)
    fillcolor: Color = dataclasses.field(default=Color.White)

    def to_dict(self) -> Dict[str, str]:
        return {
            "color": self.color.value,
            "fontcolor": self.fontcolor.value,
            "fillcolor": self.fillcolor.value,
        }

    @classmethod
    def darkgray(cls) -> "ModuleNodeStyle":
        return cls(
            color=Color.Darkgray, fontcolor=Color.Darkgray, fillcolor=Color.White,
        )


@dataclasses.dataclass(frozen=True)
class ModuleNode:
    path: ModulePath
    style: ModuleNodeStyle = dataclasses.field(default_factory=ModuleNodeStyle)

    @classmethod
    def from_str(cls, path: str) -> "ModuleNode":
        return cls(path=ModulePath(name=path))

    @classmethod
    def build(
        cls, path: ModulePath, style: Optional[ModuleNodeStyle] = None
    ) -> "ModuleNode":
        return cls(path=path, style=style or ModuleNodeStyle())

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def path_level(self) -> int:
        return self.path.path_level

    def __lt__(self, other: "ModuleNode"):
        return self.path < other.path

    def belongs_to(self, other: "ModuleNode") -> bool:
        return self.path.belongs_to(other.path)

    def limit_path_level(self, max_path_level: int) -> "ModuleNode":
        assert max_path_level > 0

        new_path = self.path.limit_path_level(max_path_level)
        return ModuleNode(new_path)

    def to_darkgray(self) -> "ModuleNode":
        return self.build(path=self.path, style=ModuleNodeStyle.darkgray())
