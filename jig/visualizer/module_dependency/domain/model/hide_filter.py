import dataclasses
from typing import List

from jig.visualizer.module_dependency.domain.value.edge_style import EdgeStyle
from jig.visualizer.module_dependency.domain.value.module_edge import ModuleEdge
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode

from jig.visualizer.module_dependency.domain.value.node_style import NodeStyle


@dataclasses.dataclass
class HideFilter:
    """ノードを非表示にするためのフィルタ"""

    nodes: List[ModuleNode] = dataclasses.field(default_factory=list)

    def add_node(self, node: ModuleNode):
        self.nodes.append(node)

    def reset(self):
        self.nodes.clear()

    def is_hidden_node(self, node: ModuleNode) -> bool:
        for n in self.nodes:
            if node.belongs_to(n):
                return True

        return False

    def is_hidden_edge(self, edge: ModuleEdge) -> bool:
        for node in self.nodes:
            if edge.tail.belongs_to(node) or edge.head.belongs_to(node):
                return True

        return False

    def filter_node_style(
        self, node: ModuleNode, current_style: NodeStyle
    ) -> NodeStyle:
        if not self.is_hidden_node(node):
            return current_style

        return current_style.with_invisible(True)

    def filter_edge_style(
        self, edge: ModuleEdge, current_style: EdgeStyle
    ) -> EdgeStyle:
        if not self.is_hidden_edge(edge):
            return current_style

        return current_style.with_invisible(True)
