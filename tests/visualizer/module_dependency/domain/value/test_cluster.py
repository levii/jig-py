from jig.visualizer.module_dependency.domain.value.cluster import Cluster
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode


def node(name: str) -> ModuleNode:
    return ModuleNode.from_str(name)


class TestCluster:
    def test_is_empty(self):
        c = Cluster(node=node("foo"))
        assert c.is_empty is True

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
