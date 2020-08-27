import dataclasses

from graphviz import Digraph

from jig.visualizer.module_dependency.domain.model.graph import Graph
from .cluster_renderer import ClusterRenderer


@dataclasses.dataclass
class GraphRenderer:
    graph: Graph

    def render(self) -> Digraph:
        d = Digraph()

        for node in sorted(self.graph.nodes):
            node_options = node.style.to_dict()
            # 描画する node の配下に位置する node が存在する場合には、 shape=rect として表示する
            if self.graph.child_node_exists(node):
                node_options["shape"] = "rect"
            d.node(name=node.path.name, **node_options)

        for edge in sorted(self.graph.edges):
            d.edge(edge.tail.name, edge.head.name, **edge.style.to_dict())

        for cluster in self.graph.clusters.values():
            cluster_renderer = ClusterRenderer(cluster)
            d.subgraph(cluster_renderer.render())

        return d
