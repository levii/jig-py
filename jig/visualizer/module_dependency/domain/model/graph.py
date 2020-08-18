import dataclasses
from typing import Set, List, Dict

from jig.visualizer.module_dependency.domain.value.cluster import Cluster
from jig.visualizer.module_dependency.domain.value.module_edge import ModuleEdge
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode


@dataclasses.dataclass
class Graph:
    nodes: Set[ModuleNode] = dataclasses.field(default_factory=set)
    edges: Set[ModuleEdge] = dataclasses.field(default_factory=set)
    clusters: Dict[ModuleNode, Cluster] = dataclasses.field(default_factory=dict)

    def add_node(self, node: ModuleNode):
        self.nodes.add(node)

    def add_edge(self, edge: ModuleEdge):
        self.edges.add(edge)

        self.add_node(edge.tail)
        self.add_node(edge.head)

    def add_cluster(self, cluster: Cluster):
        if cluster.node in self.clusters:
            raise ValueError(f"{cluster.node.name} がすでに存在します。")

        self.clusters[cluster.node] = cluster

    def remove_node(self, node: ModuleNode):
        if node in self.nodes:
            self.nodes.remove(node)

        edges = list(filter(lambda e: e.has_node(node), self.edges))
        for edge in edges:
            self.edges.remove(edge)

        self._remove_node_from_cluster(node)

    def _remove_node_from_cluster(self, node: ModuleNode):
        # Dict#values() で for を回しているときには、要素削除できないので、 List にキャストする
        for cluster in list(self.clusters.values()):
            cluster.remove(node)

            if cluster.is_empty:
                del self.clusters[cluster.node]

    def successors(self, node: ModuleNode) -> List[ModuleNode]:
        return [e.head for e in self.edges if e.tail == node]

    def predecessors(self, node: ModuleNode) -> List[ModuleNode]:
        return [e.tail for e in self.edges if e.head == node]
