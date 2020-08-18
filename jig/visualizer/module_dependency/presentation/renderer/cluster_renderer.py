import dataclasses

from graphviz import Digraph

from jig.visualizer.module_dependency.domain.value.cluster import Cluster


@dataclasses.dataclass(frozen=True)
class ClusterRenderer:
    cluster: Cluster

    def render(self) -> Digraph:
        g = Digraph(name=f"cluster_{self.cluster.node.name}")
        g.attr(label=self.cluster.node.name)

        for node in sorted(self.cluster.children):
            g.node(node.name)

        return g
