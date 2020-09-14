import dataclasses
from typing import Dict

from jig.visualizer.module_dependency.domain.value.penwidth import Color, PenWidth


@dataclasses.dataclass(frozen=True)
class EdgeStyle:
    color: Color = dataclasses.field(default=Color.Black)
    fontcolor: Color = dataclasses.field(default=Color.Black)
    penwidth: PenWidth = dataclasses.field(default=PenWidth.Normal)
    filled: bool = False
    invisible: bool = False

    def to_dict(self) -> Dict[str, str]:
        return {
            "color": self.color.value,
            "fontcolor": self.fontcolor.value,
            "penwidth": self.penwidth.to_size(self.penwidth),
            "style": self.style,
            "dir": self.dir,
        }

    @property
    def dir(self) -> str:
        # invisible edge の場合には、無向グラフとして振る舞う
        # (style="invisible" としても矢印が残ってしまうので)
        if self.invisible:
            return "none"
        return "directed"

    @property
    def style(self) -> str:
        if self.invisible:
            return "invisible"
        if self.filled:
            return "filled"

        return ""
