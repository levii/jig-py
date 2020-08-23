import dataclasses
from typing import Set, Dict, Optional

from .module_node import ModuleNode


@dataclasses.dataclass
class Cluster:
    node: ModuleNode
    children: Set[ModuleNode] = dataclasses.field(default_factory=set)
    clusters: Dict[ModuleNode, "Cluster"] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> dict:
        nodes = sorted([n.name for n in self.children])
        clusters = dict(
            [(node.name, cluster.to_dict()) for node, cluster in self.clusters.items()]
        )

        return {"nodes": nodes, "clusters": clusters}

    @property
    def is_empty(self) -> bool:
        if self.children:
            return False

        return all([cluster.is_empty for cluster in self.clusters.values()])

    def find_node_owner(self, node: ModuleNode) -> Optional["Cluster"]:
        if node in self.children:
            return self

        for cluster in self.clusters.values():
            owner = cluster.find_node_owner(node)
            if owner:
                return owner

        return None

    def add(self, node: ModuleNode):
        self.children.add(node)

    def add_cluster(self, cluster: "Cluster"):
        self.clusters[cluster.node] = cluster

    def remove(self, node: ModuleNode):
        if node in self.children:
            self.children.remove(node)

        for cluster in list(self.clusters.values()):
            cluster.remove(node)
            if cluster.is_empty:
                del self.clusters[cluster.node]

    def hide_node(self, node: ModuleNode):
        if node in self.children:
            self.children.remove(node)
            self.children.add(node.to_invisible())
