import dataclasses

from graphviz import Digraph

from jig.visualizer.module_dependency.domain.model.graph import Graph
from jig.visualizer.module_dependency.domain.value.module_edge import ModuleEdge
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode
from jig.visualizer.module_dependency.presentation.renderer.graph_renderer import (
    GraphRenderer,
)


@dataclasses.dataclass(frozen=True)
class GraphController:
    graph: Graph

    @classmethod
    def sample(cls) -> "GraphController":
        g = Graph()
        g.add_node(ModuleNode.from_str("A"))
        g.add_edge(ModuleEdge.from_str("X", "Y"))

        return cls(g)

    def remove(self, node_name: str):
        node = ModuleNode.from_str(node_name)
        self.graph.remove_node(node)

    def dig(self, node_name: str):
        pass

    def render(self) -> Digraph:
        renderer = GraphRenderer(self.graph)
        return renderer.render()
