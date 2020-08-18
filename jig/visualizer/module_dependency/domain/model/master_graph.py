import dataclasses
from typing import Optional, List, Tuple

from jig.visualizer.module_dependency.domain.value.module_edge import (
    ModuleEdge,
    ModuleEdgeCollection,
)
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode


@dataclasses.dataclass
class MasterGraph:
    edges: ModuleEdgeCollection = dataclasses.field(
        default_factory=ModuleEdgeCollection
    )

    @classmethod
    def from_tuple_list(cls, edges: List[Tuple[str, str]]) -> "MasterGraph":
        return cls(ModuleEdgeCollection.from_tuple_list(edges))

    def find_parent_edge(self, edge: ModuleEdge) -> Optional[ModuleEdge]:
        return self.edges.find_parent_edge(edge=edge)

    def find_nodes(self, node: ModuleNode) -> List[ModuleNode]:
        result = []

        for new_edge in self.edges:
            if new_edge.head.belongs_to(node):
                result.append(new_edge.head)
            if new_edge.tail.belongs_to(node):
                result.append(new_edge.tail)

        return result

    def find_edges(self, node: ModuleNode) -> List[ModuleEdge]:
        result = []

        for new_edge in self.edges:
            if new_edge.head.belongs_to(node) and new_edge.tail.belongs_to(node):
                result.append(new_edge)

        return result

    def __iter__(self):
        return iter(self.edges)
