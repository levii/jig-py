import dataclasses
from typing import Dict

from jig.visualizer.module_dependency.domain.value.penwidth import Color, PenWidth


@dataclasses.dataclass(frozen=True)
class NodeStyle:
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
        }

    def _clone(self, **changes) -> "NodeStyle":
        return dataclasses.replace(self, **changes)

    def with_penwidth(self, penwidth: PenWidth) -> "NodeStyle":
        return self._clone(penwidth=penwidth)

    @property
    def style(self) -> str:
        if self.invisible:
            return "invisible"
        if self.filled:
            return "filled"

        return ""
