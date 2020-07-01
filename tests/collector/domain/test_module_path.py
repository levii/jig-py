from jig.collector.domain import ModulePath


def mod(path: str) -> ModulePath:
    return ModulePath.from_str(path)


class TestModulePath:
    def test_from_str(self):
        p = ModulePath(names=["jig", "collector", "domain"])
        assert p == ModulePath.from_str("jig.collector.domain")

    def test_str(self):
        p = mod("jig.collector.domain")
        assert str(p) == "jig.collector.domain"

    def test_join(self):
        p = mod("jig.collector.domain")
        assert p.join("mod") == mod("jig.collector.domain.mod")
