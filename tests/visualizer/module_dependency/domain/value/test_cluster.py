from jig.visualizer.module_dependency.domain.value.cluster import Cluster
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode


def node(name: str) -> ModuleNode:
    return ModuleNode.from_str(name)


class TestCluster:
    def test_is_empty(self):
        c = Cluster(node=node("foo"))
        assert c.is_empty is True

        child_cluster = Cluster(node=node("bar"))
        c.add_cluster(child_cluster)

        assert c.is_empty is True

        child_cluster.add(node("buzz"))
        assert c.is_empty is False

    def test_descendant_nodes(self):
        c = Cluster(node=node("jig"))
        assert c.descendant_nodes() == []

        c.add(node("jig.cli"))
        assert c.descendant_nodes() == [node("jig.cli")]

        child_cluster = Cluster(
            node=node("jig.collection"),
            children={node("jig.collector.domain"), node("jig.collector.application")},
        )
        c.add_cluster(child_cluster)

        assert c.descendant_nodes() == [
            node("jig.collector.application"),
            node("jig.collector.domain"),
            node("jig.cli"),
        ]

    def test_find_cluster(self):
        c = Cluster(node=node("jig"), children={node("jig.cli")})

        child_cluster = Cluster(
            node=node("jig.collector"), children={node("jig.collector.application")}
        )
        c.add_cluster(child_cluster)

        assert c.find_cluster(node("x")) is None
        assert c.find_cluster(node("jig")) is None
        assert c.find_cluster(node("jig.collector")) is child_cluster

    def test_find_node_owner(self):
        c = Cluster(node=node("jig"), children={node("jig.cli")})

        child_cluster = Cluster(
            node=node("jig.collector"), children={node("jig.collector.application")}
        )
        c.add_cluster(child_cluster)

        assert c.find_node_owner(node("foo")) is None
        assert c.find_node_owner(node("jig")) is None
        assert c.find_node_owner(node("jig.cli")) == c
        assert c.find_node_owner(node("jig.collector.application")) == child_cluster

    def test_add(self):
        c = Cluster(node=node("foo"))
        c.add(node=node("bar"))
        assert c.is_empty is False

    def test_remove(self):
        c = Cluster(node=node("foo"), children={node("bar")})
        c.remove(node=node("bar"))
        assert c.is_empty is True

        c.remove(node=node("baz"))
        assert c.is_empty is True

    def test_remove_with_child_cluster(self):
        c = Cluster(node=node("jig"), children={node("jig.cli")})

        child_cluster = Cluster(
            node=node("jig.collector"), children={node("jig.collector.application")}
        )
        c.add_cluster(child_cluster)

        c.remove(node=node("jig.collector.application"))
        assert len(c.clusters) == 0
