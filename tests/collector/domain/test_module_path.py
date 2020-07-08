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

    def test_add(self):
        m1 = mod("aaa.bbb")
        m2 = mod("xxx.yyy")

        assert m1 + m2 == mod("aaa.bbb.xxx.yyy")
        assert m2 + m1 == mod("xxx.yyy.aaa.bbb")

    def test_belongs_to(self):
        m1 = mod("aaa.bbb")
        m2 = mod("aaa.bbb.ccc")

        assert m1.belongs_to(m1)
        assert not m1.belongs_to(m2)
        assert m2.belongs_to(m1)

    def test_depth(self):
        assert mod("aaa").depth == 1
        assert mod("aaa.bbb").depth == 2
        assert mod("aaa.bbb.ccc").depth == 3

    def test_path_in_depth(self):
        assert mod("aaa.bbb.ccc").path_in_depth(1) == mod("aaa")
        assert mod("aaa.bbb.ccc").path_in_depth(2) == mod("aaa.bbb")
        assert mod("aaa.bbb.ccc").path_in_depth(3) == mod("aaa.bbb.ccc")
        assert mod("aaa.bbb.ccc").path_in_depth(4) == mod("aaa.bbb.ccc")
