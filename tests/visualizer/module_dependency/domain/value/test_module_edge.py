from jig.visualizer.module_dependency.domain.value.module_edge import ModuleEdge


def edge(tail: str, head: str) -> ModuleEdge:
    return ModuleEdge.from_str(tail, head)


class TestModuleEdge:
    def test_limit_path_level(self):
        e = edge("a.b", "x.y.z")

        assert e.limit_path_level(1) == edge("a", "x")
        assert e.limit_path_level(2) == edge("a.b", "x.y")
        assert e.limit_path_level(3) == edge("a.b", "x.y.z")
        assert e.limit_path_level(4) == edge("a.b", "x.y.z")
