import dataclasses

from jig.visualizer.module_dependency.domain.value.edge_style import EdgeStyle
from jig.visualizer.module_dependency.domain.value.module_path import ModulePath


@dataclasses.dataclass(frozen=True)
class ModuleEdgeStyle:
    tail: ModulePath
    head: ModulePath
    style: EdgeStyle = dataclasses.field(default_factory=EdgeStyle)

    def has_same_edge(self, other: "ModuleEdgeStyle") -> bool:
        return self.tail == other.tail and self.head == other.head
