from jig.collector.domain import ImportPath


def path(path: str) -> ImportPath:
    return ImportPath.from_str(path)


class TestImportPath:
    def test_from_str(self):
        p = ImportPath(names=["jig", "collector", "domain"])
        assert p == ImportPath.from_str("jig.collector.domain")

    def test_str(self):
        p = path("jig.collector.domain")
        assert str(p) == "jig.collector.domain"

    def test_join(self):
        p = path("jig.collector.domain")
        assert p.join("mod") == path("jig.collector.domain.mod")

    def test_add(self):
        m1 = path("aaa.bbb")
        m2 = path("xxx.yyy")

        assert m1 + m2 == path("aaa.bbb.xxx.yyy")
        assert m2 + m1 == path("xxx.yyy.aaa.bbb")

    def test_belongs_to(self):
        m1 = path("aaa.bbb")
        m2 = path("aaa.bbb.ccc")

        assert m1.belongs_to(m1)
        assert not m1.belongs_to(m2)
        assert m2.belongs_to(m1)

    def test_depth(self):
        assert path("aaa").depth == 1
        assert path("aaa.bbb").depth == 2
        assert path("aaa.bbb.ccc").depth == 3

    def test_path_in_depth(self):
        assert path("aaa.bbb.ccc").path_in_depth(1) == path("aaa")
        assert path("aaa.bbb.ccc").path_in_depth(2) == path("aaa.bbb")
        assert path("aaa.bbb.ccc").path_in_depth(3) == path("aaa.bbb.ccc")
        assert path("aaa.bbb.ccc").path_in_depth(4) == path("aaa.bbb.ccc")
