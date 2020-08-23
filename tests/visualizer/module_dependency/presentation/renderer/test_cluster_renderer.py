from graphviz import Digraph

from jig.visualizer.module_dependency.domain.value.cluster import Cluster
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode
from jig.visualizer.module_dependency.presentation.renderer.cluster_renderer import (
    ClusterRenderer,
)


def node(name: str) -> ModuleNode:
    return ModuleNode.from_str(name)


class TestClusterRenderer:
    def test_render(self):
        cluster = Cluster(
            node=node("jig"), children={node("jig.collector"), node("jig.analyzer")},
        )
        renderer = ClusterRenderer(cluster=cluster)

        g = Digraph(name="cluster_jig")
        g.attr(label="jig")
        g.node("jig.analyzer")
        g.node("jig.collector")

        assert str(renderer.render()) == str(g)

    def test_render__clusters(self):
        cluster = Cluster(node=node("jig"), children={node("jig.analyzer")})
        sub_cluster = Cluster(
            node=node("jig.collector"),
            children={node("jig.collector.application"), node("jig.collector.domain")},
        )
        cluster.add_cluster(sub_cluster)
        renderer = ClusterRenderer(cluster=cluster)

        g = Digraph(name="cluster_jig")
        g.attr(label="jig")
        g.node("jig.analyzer")

        sub = Digraph(name="cluster_jig.collector")
        sub.attr(label="jig.collector")
        sub.node("jig.collector.application")
        sub.node("jig.collector.domain")

        g.subgraph(sub)

        assert str(renderer.render()) == str(g)
