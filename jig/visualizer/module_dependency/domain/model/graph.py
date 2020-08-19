import dataclasses
from typing import Set, List, Dict

from jig.visualizer.module_dependency.domain.model.master_graph import MasterGraph
from jig.visualizer.module_dependency.domain.value.cluster import Cluster
from jig.visualizer.module_dependency.domain.value.module_edge import (
    ModuleEdge,
    ModuleEdgeCollection,
)
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode


@dataclasses.dataclass
class Graph:
    master_graph: MasterGraph = dataclasses.field(default_factory=MasterGraph)
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
        not_included = cluster.children - self.nodes
        if not_included:
            raise ValueError(f"Graphのnodesに含まれないchildrenがあります: {not_included}")

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

    def dig(self, node: ModuleNode):

        self._dig_successors(node)
        self._dig_predecessors(node)
        self._dig_inner_edge(node)
        self._dig_clustering(node)

        self.remove_node(node)

    def _dig_inner_edge(self, node: ModuleNode):
        for edge in self.master_graph.find_edges(node):
            self.add_edge(edge)

    def _dig_clustering(self, node: ModuleNode):
        cluster = Cluster(node=node)
        for n in self.master_graph.find_nodes(node):
            cluster.add(n)

        self.add_cluster(cluster)

    def _dig_successors(self, node: ModuleNode):
        # 現在のnodeからの接続先エッジを取得
        current_edges = ModuleEdgeCollection(
            [ModuleEdge(node, s) for s in self.successors(node)]
        )

        for new_edge in self.master_graph:
            parent_edge = current_edges.find_parent_edge(new_edge)

            if parent_edge:
                # ノード分解した新しいノードから、ノード分解していないノードへつなぐ
                edge = ModuleEdge(new_edge.tail, parent_edge.head)
                self.add_edge(edge)

    def _dig_predecessors(self, node: ModuleNode):
        # 現在のnodeからの接続元エッジを取得
        current_edges = ModuleEdgeCollection(
            [ModuleEdge(p, node) for p in self.predecessors(node)]
        )

        for new_edge in self.master_graph:
            parent_edge = current_edges.find_parent_edge(new_edge)

            if parent_edge:
                # ノード分解した新しいノードから、ノード分解していないノードへつなぐ
                edge = ModuleEdge(parent_edge.tail, new_edge.head)
                self.add_edge(edge)
