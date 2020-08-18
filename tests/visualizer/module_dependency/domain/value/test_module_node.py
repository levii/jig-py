from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode


def node(name: str) -> ModuleNode:
    return ModuleNode.from_str(name)


class TestModuleNode:
    def test_path_level(self):
        assert node("a").path_level == 1
        assert node("ab").path_level == 1
        assert node("a.b.c").path_level == 3

    def test_limit_path_level(self):
        n = node("a.b.c")
        assert n.limit_path_level(1) == node("a")
        assert n.limit_path_level(2) == node("a.b")
        assert n.limit_path_level(3) == node("a.b.c")
        assert n.limit_path_level(4) == node("a.b.c")
