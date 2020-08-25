import dataclasses
from typing import Optional, List, Tuple, Dict

from .penwidth import Color, PenWidth
from .module_node import ModuleNode


@dataclasses.dataclass(frozen=True)
class ModuleEdgeStyle:
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


@dataclasses.dataclass(frozen=True)
class ModuleEdge:
    tail: ModuleNode
    head: ModuleNode
    style: ModuleEdgeStyle = dataclasses.field(
        default_factory=ModuleEdgeStyle, compare=False
    )

    @classmethod
    def from_str(cls, tail: str, head: str) -> "ModuleEdge":
        return cls(tail=ModuleNode.from_str(tail), head=ModuleNode.from_str(head))

    @classmethod
    def build(
        cls, tail: ModuleNode, head: ModuleNode, style: Optional[ModuleEdgeStyle] = None
    ) -> "ModuleEdge":
        return cls(tail=tail, head=head, style=style or ModuleEdgeStyle())

    def belongs_to(self, other: "ModuleEdge") -> bool:
        return self.tail.belongs_to(other.tail) and self.head.belongs_to(other.head)

    def has_node(self, node: ModuleNode) -> bool:
        return node == self.tail or node == self.head

    def is_self_loop(self) -> bool:
        return self.tail == self.head

    def limit_path_level(self, max_path_level: int) -> "ModuleEdge":
        assert max_path_level > 0

        new_tail = self.tail.limit_path_level(max_path_level)
        new_head = self.head.limit_path_level(max_path_level)
        return ModuleEdge(tail=new_tail, head=new_head)

    def __lt__(self, other: "ModuleEdge"):
        if self.head == other.head:
            return self.tail < other.tail

        return self.head < other.head

    def build_reverse(self) -> "ModuleEdge":
        return self.build(tail=self.head, head=self.tail, style=self.style)

    def to_invisible(self) -> "ModuleEdge":
        return self.build(
            tail=self.tail, head=self.head, style=ModuleEdgeStyle(invisible=True)
        )

    def with_style(self, style: ModuleEdgeStyle) -> "ModuleEdge":
        return self.build(tail=self.tail, head=self.head, style=style)

    def reset_style(self) -> "ModuleEdge":
        return self.build(tail=self.tail, head=self.head)


@dataclasses.dataclass(frozen=True)
class ModuleEdgeCollection:
    _edges: List[ModuleEdge] = dataclasses.field(default_factory=list)

    @classmethod
    def from_tuple_list(cls, edges: List[Tuple[str, str]]) -> "ModuleEdgeCollection":
        return cls([ModuleEdge.from_str(tail=e[0], head=e[1]) for e in edges])

    def find_parent_edge(self, edge: ModuleEdge) -> Optional[ModuleEdge]:
        for e in self._edges:
            if edge.belongs_to(e):
                return e
        return None

    def __iter__(self):
        return iter(self._edges)
