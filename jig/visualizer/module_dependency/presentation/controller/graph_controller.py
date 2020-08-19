import dataclasses

from graphviz import Digraph

from jig.visualizer.module_dependency.domain.model.graph import Graph
from jig.visualizer.module_dependency.domain.model.master_graph import MasterGraph
from jig.visualizer.module_dependency.domain.value.module_edge import (
    ModuleEdge,
    ModuleEdgeCollection,
)
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode
from jig.visualizer.module_dependency.presentation.renderer.graph_renderer import (
    GraphRenderer,
)


@dataclasses.dataclass(frozen=True)
class GraphController:
    graph: Graph

    @classmethod
    def sample(cls) -> "GraphController":
        master_graph = MasterGraph(
            edges=ModuleEdgeCollection(
                [ModuleEdge.from_str("A.A", "B.B"), ModuleEdge.from_str("X.A", "Y.B")]
            )
        )

        g = Graph(master_graph=master_graph)
        g.add_edge(ModuleEdge.from_str("A", "B"))
        g.add_edge(ModuleEdge.from_str("X", "Y"))

        return cls(g)

    def remove(self, node_name: str):
        node = ModuleNode.from_str(node_name)
        self.graph.remove_node(node)

    def dig(self, node_name: str):
        node = ModuleNode.from_str(node_name)
        self.graph.dig(node)

    def render(self) -> Digraph:
        renderer = GraphRenderer(self.graph)
        return renderer.render()
