from typing import Set

import pytest

from jig.visualizer.module_dependency.domain.model.graph import Graph
from jig.visualizer.module_dependency.domain.model.master_graph import MasterGraph
from jig.visualizer.module_dependency.domain.value.cluster import Cluster
from jig.visualizer.module_dependency.domain.value.module_edge import ModuleEdge
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode


def node(name: str) -> ModuleNode:
    return ModuleNode.from_str(name)


def edge(tail: str, head: str) -> ModuleEdge:
    return ModuleEdge.from_str(tail, head)


def cluster(name: str, children: Set[str]) -> Cluster:
    return Cluster(node=node(name), children=set([node(name) for name in children]))


class TestGraph:
    def test_add_node(self):
        g = Graph()
        g.add_node(node("A"))

        assert len(g.nodes) == 1
        assert g.nodes == {node("A")}

        g.add_node(node("A"))

        assert len(g.nodes) == 1
        assert g.nodes == {node("A")}

    def test_add_edge(self):
        g = Graph()
        g.add_edge(edge("A", "B"))

        assert len(g.edges) == 1
        assert len(g.nodes) == 2
        assert g.nodes == {node("A"), node("B")}
        assert g.edges == {edge("A", "B")}

        g.add_edge(edge("A", "B"))

        assert len(g.edges) == 1

    def test_add_cluster(self):
        g = Graph()
        g.add_edge(edge("A", "B"))
        g.add_cluster(cluster("pkg", {"A", "B"}))

        assert len(g.clusters) == 1

        with pytest.raises(ValueError):
            g.add_cluster(cluster("pkg", {"C"}))

    def test_remove_node(self):
        g = Graph()
        g.add_edge(edge("A", "B"))

        assert len(g.edges) == 1
        assert len(g.nodes) == 2

        g.remove_node(node("A"))
        assert len(g.edges) == 0
        assert len(g.nodes) == 1

    def test_remove_node_from_cluster(self):
        g = Graph()
        g.add_edge(edge("A", "B"))
        g.add_cluster(cluster("pkg", {"A"}))
        assert len(g.clusters) == 1

        g.remove_node(node("A"))
        assert len(g.clusters) == 0

    def test_successors(self):
        g = Graph()
        g.add_edge(edge("A", "B"))

        assert g.successors(node("A")) == [node("B")]
        assert g.successors(node("B")) == []
        assert g.successors(node("C")) == []

    def test_predecessors(self):
        g = Graph()
        g.add_edge(edge("A", "B"))

        assert g.predecessors(node("A")) == []
        assert g.predecessors(node("B")) == [node("A")]
        assert g.predecessors(node("C")) == []

    def test_dig(self):
        master_graph = MasterGraph.from_tuple_list(
            [
                ("jig.collector.application", "jig.collector.domain.source_code"),
                ("jig.collector.application", "jig.collector.domain.source_file"),
                (
                    "jig.collector.domain.source_code",
                    "jig.collector.domain.source_file",
                ),
            ]
        )
        g = Graph(master_graph=master_graph)
        g.add_edge(edge("jig.collector.application", "jig.collector.domain"))

        assert len(g.nodes) == 2
        assert len(g.edges) == 1
        assert len(g.clusters) == 0
        assert set([n.name for n in g.nodes]) == {
            "jig.collector.application",
            "jig.collector.domain",
        }
        assert set([(e.tail.name, e.head.name) for e in g.edges]) == {
            ("jig.collector.application", "jig.collector.domain"),
        }

        g.dig(node("jig.collector.domain"))

        assert len(g.nodes) == 3
        assert len(g.edges) == 3
        assert len(g.clusters) == 1

        assert set([n.name for n in g.nodes]) == {
            "jig.collector.application",
            "jig.collector.domain.source_code",
            "jig.collector.domain.source_file",
        }
        assert set([(e.tail.name, e.head.name) for e in g.edges]) == {
            ("jig.collector.application", "jig.collector.domain.source_code"),
            ("jig.collector.application", "jig.collector.domain.source_file"),
            ("jig.collector.domain.source_code", "jig.collector.domain.source_file"),
        }
        domain_cluster = g.clusters[node("jig.collector.domain")]
        assert domain_cluster.node == node("jig.collector.domain")
        assert set([n.name for n in domain_cluster.children]) == {
            "jig.collector.domain.source_code",
            "jig.collector.domain.source_file",
        }
