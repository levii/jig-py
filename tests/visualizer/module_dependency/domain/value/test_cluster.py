from jig.visualizer.module_dependency.domain.value.cluster import Cluster
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode
from jig.visualizer.module_dependency.domain.value.module_path import ModulePath


def path(name: str) -> ModulePath:
    return ModulePath(name)


def node(name: str) -> ModuleNode:
    return ModuleNode.from_str(name)


class TestCluster:
    def test_is_empty(self):
        c = Cluster(module_path=path("foo"))
        assert c.is_empty is True

        child_cluster = Cluster(module_path=path("bar"))
        c.add_cluster(child_cluster)

        assert c.is_empty is True

        child_cluster.add(node("buzz"))
        assert c.is_empty is False

    def test_list_all_modules(self):
        c = Cluster(module_path=path("foo"), children={node("foo.foo")})
        assert c.list_all_modules() == [path("foo"), path("foo.foo")]

        child_cluster = Cluster(module_path=path("bar"), children={node("bar.bar")})
        c.add_cluster(child_cluster)

        assert c.list_all_modules() == [
            path("bar"),
            path("bar.bar"),
            path("foo"),
            path("foo.foo"),
        ]

        grand_child_cluster = Cluster(
            module_path=path("buzz"), children={node("buzz.buzz")}
        )
        child_cluster.add_cluster(grand_child_cluster)
        assert c.list_all_modules() == [
            path("bar"),
            path("bar.bar"),
            path("buzz"),
            path("buzz.buzz"),
            path("foo"),
            path("foo.foo"),
        ]

    def test_descendant_nodes(self):
        c = Cluster(module_path=path("jig"))
        assert c.descendant_nodes() == []

        c.add(node("jig.cli"))
        assert c.descendant_nodes() == [node("jig.cli")]

        child_cluster = Cluster(
            module_path=path("jig.collection"),
            children={node("jig.collector.domain"), node("jig.collector.application")},
        )
        c.add_cluster(child_cluster)

        assert c.descendant_nodes() == [
            node("jig.collector.application"),
            node("jig.collector.domain"),
            node("jig.cli"),
        ]

    def test_find_cluster(self):
        c = Cluster(module_path=path("jig"), children={node("jig.cli")})

        child_cluster = Cluster(
            module_path=path("jig.collector"),
            children={node("jig.collector.application")},
        )
        c.add_cluster(child_cluster)

        assert c.find_cluster(node("x")) is None
        assert c.find_cluster(node("jig")) is None
        assert c.find_cluster(node("jig.collector")) is child_cluster

    def test_find_node_owner(self):
        c = Cluster(module_path=path("jig"), children={node("jig.cli")})

        child_cluster = Cluster(
            module_path=path("jig.collector"),
            children={node("jig.collector.application")},
        )
        c.add_cluster(child_cluster)

        assert c.find_node_owner(node("foo")) is None
        assert c.find_node_owner(node("jig")) is None
        assert c.find_node_owner(node("jig.cli")) == c
        assert c.find_node_owner(node("jig.collector.application")) == child_cluster

    def test_add(self):
        c = Cluster(module_path=path("foo"))
        c.add(node=node("bar"))
        assert c.is_empty is False

    def test_remove(self):
        c = Cluster(module_path=path("foo"), children={node("bar")})
        c.remove(node=node("bar"))
        assert c.is_empty is True

        c.remove(node=node("baz"))
        assert c.is_empty is True

    def test_remove_with_child_cluster(self):
        c = Cluster(module_path=path("jig"), children={node("jig.cli")})

        child_cluster = Cluster(
            module_path=path("jig.collector"),
            children={node("jig.collector.application")},
        )
        c.add_cluster(child_cluster)

        c.remove(node=node("jig.collector.application"))
        assert len(c.clusters) == 0
