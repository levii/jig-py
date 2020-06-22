from jig.collector.domain.ast import Import, ImportFrom, JigAST


class TestJigASTImport:
    def test_simple_import(self):
        source = """
import dataclasses

@dataclasses.dataclass(frozen=True)
class Sample:
    value: str
        """

        imports = JigAST.parse(source).imports()

        assert len(imports) == 1
        assert isinstance(imports[0], Import)
        assert len(imports[0].names) == 1
        assert imports[0].names[0].name == "dataclasses"

    def test_simple_import_from(self):
        source = """
from typing import Optional
        """

        nodes = JigAST.parse(source).import_froms()

        assert len(nodes) == 1
        assert isinstance(nodes[0], ImportFrom)
        assert len(nodes[0].names) == 1
        assert nodes[0].module == "typing"
        assert nodes[0].names[0].name == "Optional"
        assert nodes[0].level == 0
