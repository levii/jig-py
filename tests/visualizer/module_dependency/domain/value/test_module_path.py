from jig.visualizer.module_dependency.domain.value.module_path import ModulePath


def module_path(name: str) -> ModulePath:
    return ModulePath(name)


class TestModulePath:
    def test_path_level(self):
        assert module_path("a").path_level == 1
        assert module_path("foo").path_level == 1
        assert module_path("a.b.c").path_level == 3

    def test_belongs_to(self):
        assert module_path("a").belongs_to(module_path("a"))
        assert module_path("a.a").belongs_to(module_path("a"))
        assert not module_path("a").belongs_to(module_path("a.a"))

    def test_limit_path_level(self):
        p1 = module_path("a.b.c")

        assert p1.limit_path_level(1) == module_path("a")
        assert p1.limit_path_level(2) == module_path("a.b")
        assert p1.limit_path_level(3) == module_path("a.b.c")
        assert p1.limit_path_level(4) == module_path("a.b.c")
