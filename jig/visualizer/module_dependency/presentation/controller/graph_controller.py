import dataclasses

from graphviz import Digraph

from jig.visualizer.module_dependency.domain.model.graph import Graph
from jig.visualizer.module_dependency.domain.model.master_graph import MasterGraph
from jig.visualizer.module_dependency.domain.value.module_edge import (
    ModuleEdge,
    ModuleEdgeCollection,
)
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode
from jig.visualizer.module_dependency.domain.value.penwidth import Color, PenWidth
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

    def remove(self, *node_names: str) -> "GraphController":
        for node_name in node_names:
            node = ModuleNode.from_str(node_name)
            self.graph.remove_node(node)
        return self

    def dig(self, *node_names: str) -> "GraphController":
        for node_name in node_names:
            node = ModuleNode.from_str(node_name)
            self.graph.dig(node)
        return self

    def render(self) -> Digraph:
        renderer = GraphRenderer(self.graph)
        return renderer.render()

    def reset(self) -> "GraphController":
        self.graph.reset()
        return self

    def hide(self, *node_names: str) -> "GraphController":
        for node_name in node_names:
            node = ModuleNode.from_str(node_name)
            self.graph.hide_node(node)
        return self

    def style(
        self,
        *node_names: str,
        color: str = "black",
        fontcolor: str = "black",
        penwidth: str = "normal",
    ) -> "GraphController":
        color_ = Color(color)
        fontcolor_ = Color(fontcolor)
        penwidth_ = PenWidth(penwidth)

        for node_name in node_names:
            node = ModuleNode.from_str(node_name)
            self.graph.style(
                node=node, color=color_, fontcolor=fontcolor_, penwidth=penwidth_
            )
        return self

    def reset_style(self) -> "GraphController":
        self.graph.reset_style()
        return self

    def auto_highlight(self) -> "GraphController":
        self.graph.auto_highlight()
        return self

    def _repr_svg_(self):
        """
        Jupyter 上でオブジェクト自身を評価したときグラフ描画されるようにする。

        https://ipython.readthedocs.io/en/stable/config/integrating.html#rich-display
        :return:
        """
        g = self.render()

        # graphvizの実装に移譲する
        return g._repr_svg_()
