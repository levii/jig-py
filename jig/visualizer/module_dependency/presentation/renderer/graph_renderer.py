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
            d.node(name=node.path.name)

        for edge in sorted(self.graph.edges):
            d.edge(edge.tail.name, edge.head.name)

        for cluster in self.graph.clusters.values():
            cluster_renderer = ClusterRenderer(cluster)
            d.subgraph(cluster_renderer.render())

        return d
