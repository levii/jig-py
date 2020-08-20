from jig.visualizer.module_dependency.domain.value.module_edge import (
    ModuleEdge,
    ModuleEdgeCollection,
)


def edge(tail: str, head: str) -> ModuleEdge:
    return ModuleEdge.from_str(tail, head)


class TestModuleEdge:
    def test_limit_path_level(self):
        e = edge("a.b", "x.y.z")

        assert e.limit_path_level(1) == edge("a", "x")
        assert e.limit_path_level(2) == edge("a.b", "x.y")
        assert e.limit_path_level(3) == edge("a.b", "x.y.z")
        assert e.limit_path_level(4) == edge("a.b", "x.y.z")

    def test_belongs_to(self):
        e = edge("a.b", "x.y.z")

        assert e.belongs_to(edge("a.b", "x.y.z")) is True
        assert e.belongs_to(edge("a", "x")) is True
        assert e.belongs_to(edge("a", "x.y.z")) is True

        assert e.belongs_to(edge("a.b.c", "x.y.z")) is False
        assert e.belongs_to(edge("a.b.c", "x")) is False

    def test_is_self_loop(self):
        assert edge("jig", "jig").is_self_loop() is True
        assert edge("jig.cli", "jig.cli").is_self_loop() is True
        assert edge("jig", "jig.cli").is_self_loop() is False


class TestModuleEdgeCollection:
    def test_find_parent_edge(self):
        c = ModuleEdgeCollection([edge("a.b", "x.y")])

        assert c.find_parent_edge(edge("a.b", "x.y.z")) == edge("a.b", "x.y")
