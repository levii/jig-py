from collector.jig_ast import Import
from collector.jig_ast import JigAST


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
