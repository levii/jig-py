import dataclasses
from typing import Set, Dict, Optional, List

from jig.visualizer.module_dependency.domain.value.module_path import ModulePath
from .module_node import ModuleNode


@dataclasses.dataclass
class Cluster:
    module_path: ModulePath
    children: Set[ModuleNode] = dataclasses.field(default_factory=set)
    clusters: Dict[ModulePath, "Cluster"] = dataclasses.field(default_factory=dict)

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

    def list_all_modules(self) -> List[ModulePath]:
        modules = {self.module_path}
        modules.update([node.path for node in self.children])

        for cluster in self.clusters.values():
            modules.update(cluster.list_all_modules())

        return sorted(modules)

    def descendant_nodes(self) -> List[ModuleNode]:
        """
        クラスタに含まれる子孫ノード（子クラスタのノードを含む）を返す。
        :return:
        """
        nodes = []
        for cluster in self.clusters.values():
            nodes += cluster.descendant_nodes()

        for node in sorted(self.children):
            nodes.append(node)

        return nodes

    def find_cluster(self, path: ModulePath) -> Optional["Cluster"]:
        for cluster in self.clusters.values():
            if cluster.module_path == path:
                return cluster

            sub_cluster = cluster.find_cluster(path)
            if sub_cluster:
                return sub_cluster

        return None

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
        self.clusters[cluster.module_path] = cluster

    def remove(self, node: ModuleNode):
        if node in self.children:
            self.children.remove(node)

        for cluster in list(self.clusters.values()):
            cluster.remove(node)
            if cluster.is_empty:
                del self.clusters[cluster.module_path]

    def hide_node(self, node: ModuleNode):
        if node in self.children:
            self.children.remove(node)
            self.children.add(node.to_invisible())

    def has_cluster(self, node: ModuleNode) -> bool:
        if node in self.clusters:
            return True

        for cluster in self.clusters.values():
            if cluster.has_cluster(node):
                return True

        return False
