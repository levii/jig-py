from graphviz import Digraph

from jig.visualizer.module_dependency.domain.model.graph import Graph
from jig.visualizer.module_dependency.domain.model.master_graph import MasterGraph
from jig.visualizer.module_dependency.domain.value.cluster import Cluster
from jig.visualizer.module_dependency.domain.value.module_edge import (
    ModuleEdge,
    ModuleEdgeStyle,
)
from jig.visualizer.module_dependency.domain.value.module_node import (
    ModuleNode,
    ModuleNodeStyle,
)
from jig.visualizer.module_dependency.domain.value.module_path import ModulePath
from jig.visualizer.module_dependency.domain.value.penwidth import Color, PenWidth
from jig.visualizer.module_dependency.presentation.renderer.graph_renderer import (
    GraphRenderer,
)


def path(name: str) -> ModulePath:
    return ModulePath(name)


def node(name: str) -> ModuleNode:
    return ModuleNode.from_str(name)


def edge(tail: str, head: str) -> ModuleEdge:
    return ModuleEdge.from_str(tail, head)


class TestGraphRenderer:
    def test_render(self):
        cluster = Cluster(module_path=path("jig"), children={node("jig.analyzer")})
        sub_cluster = Cluster(
            module_path=path("jig.collector"),
            children={node("jig.collector.application"), node("jig.collector.domain")},
        )
        cluster.add_cluster(sub_cluster)

        graph = Graph()
        graph.add_edge(edge("jig.analyzer", "jig.collector"))
        graph.add_cluster(cluster)

        renderer = GraphRenderer(graph=graph)

        g = Digraph()

        node_style = ModuleNodeStyle().to_dict()
        g.node("jig.analyzer", **node_style)
        g.node("jig.collector", **node_style)

        edge_style = ModuleEdgeStyle().to_dict()
        g.edge("jig.analyzer", "jig.collector", **edge_style)

        child = Digraph(name="cluster_jig")
        child.attr(label="jig")
        child.node("jig.analyzer")

        grandchild = Digraph(name="cluster_jig.collector")
        grandchild.attr(label="jig.collector")
        grandchild.node("jig.collector.application")
        grandchild.node("jig.collector.domain")

        child.subgraph(grandchild)
        g.subgraph(child)

        assert str(renderer.render()) == str(g)

    def test_render__with_style(self):
        master_graph = MasterGraph.from_tuple_list([("a", "b"), ("b", "c")])
        graph = Graph(master_graph)

        graph.style(
            node("b"), color=Color.Blue, fontcolor=Color.Red, penwidth=PenWidth.Bold
        )
        renderer = GraphRenderer(graph=graph)

        g = Digraph()
        default_node_style = ModuleNodeStyle().to_dict()
        node_style = ModuleNodeStyle().to_dict()
        node_style.update(
            {
                "color": "blue",
                "fontcolor": "red",
                "penwidth": PenWidth.to_size(PenWidth.Bold),
            }
        )
        g.node("a", **default_node_style)
        g.node("b", **node_style)
        g.node("c", **default_node_style)

        edge_style = ModuleEdgeStyle().to_dict()
        edge_style.update(
            {
                "color": "blue",
                "fontcolor": "red",
                "penwidth": PenWidth.to_size(PenWidth.Bold),
            }
        )
        g.edge("a", "b", **edge_style)
        g.edge("b", "c", **edge_style)

        assert str(renderer.render()) == str(g)

    def test_render__with_edge_style(self):
        master_graph = MasterGraph.from_tuple_list([("a", "b"), ("b", "c")])
        graph = Graph(master_graph)

        graph.edge_style(node("a"), node("b"), color=Color.Red, penwidth=PenWidth.Thin)
        renderer = GraphRenderer(graph=graph)

        g = Digraph()
        default_node_style = ModuleNodeStyle().to_dict()
        g.node("a", **default_node_style)
        g.node("b", **default_node_style)
        g.node("c", **default_node_style)

        default_edge_style = ModuleEdgeStyle().to_dict()
        edge_style = ModuleEdgeStyle().to_dict()
        edge_style.update({"color": "red", "penwidth": PenWidth.to_size(PenWidth.Thin)})
        g.edge("a", "b", **edge_style)
        g.edge("b", "c", **default_edge_style)

        assert str(renderer.render()) == str(g)

    def test_render__reset_style(self):
        master_graph = MasterGraph.from_tuple_list([("a", "b"), ("b", "c")])
        graph = Graph(master_graph)

        graph.style(
            node("b"), color=Color.Blue, fontcolor=Color.Red, penwidth=PenWidth.Bold
        )
        graph.reset_style()
        renderer = GraphRenderer(graph=graph)

        g = Digraph()
        default_node_style = ModuleNodeStyle().to_dict()
        g.node("a", **default_node_style)
        g.node("b", **default_node_style)
        g.node("c", **default_node_style)

        default_edge_style = ModuleEdgeStyle().to_dict()
        g.edge("a", "b", **default_edge_style)
        g.edge("b", "c", **default_edge_style)

        assert str(renderer.render()) == str(g)
