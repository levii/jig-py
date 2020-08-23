from graphviz import Digraph

from jig.visualizer.module_dependency.domain.model.graph import Graph
from jig.visualizer.module_dependency.domain.value.cluster import Cluster
from jig.visualizer.module_dependency.domain.value.module_edge import (
    ModuleEdge,
    ModuleEdgeStyle,
)
from jig.visualizer.module_dependency.domain.value.module_node import (
    ModuleNode,
    ModuleNodeStyle,
)
from jig.visualizer.module_dependency.presentation.renderer.graph_renderer import (
    GraphRenderer,
)


def node(name: str) -> ModuleNode:
    return ModuleNode.from_str(name)


def edge(tail: str, head: str) -> ModuleEdge:
    return ModuleEdge.from_str(tail, head)


class TestGraphRenderer:
    def test_render(self):
        cluster = Cluster(node=node("jig"), children={node("jig.analyzer")})
        sub_cluster = Cluster(
            node=node("jig.collector"),
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
