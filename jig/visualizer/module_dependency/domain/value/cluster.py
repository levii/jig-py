import dataclasses
from typing import Set, Dict

from .module_node import ModuleNode


@dataclasses.dataclass
class Cluster:
    node: ModuleNode
    children: Set[ModuleNode] = dataclasses.field(default_factory=set)
    clusters: Dict[ModuleNode, "Cluster"] = dataclasses.field(default_factory=dict)

    def to_dict(self) -> dict:
        nodes = sorted([n.name for n in self.children])

        return {"nodes": nodes}

    @property
    def is_empty(self) -> bool:
        return not bool(self.children)

    def add(self, node: ModuleNode):
        self.children.add(node)

    def add_cluster(self, cluster: "Cluster"):
        self.clusters[cluster.node] = cluster

    def remove(self, node: ModuleNode):
        if node in self.children:
            self.children.remove(node)

    def hide_node(self, node: ModuleNode):
        if node in self.children:
            self.children.remove(node)
            self.children.add(node.to_darkgray())
