from typed_ast import ast3 as ast
from jig.collector.jig_ast import ImportFrom


def parse_import_from(line: str) -> ImportFrom:
    import_from_ast = ast.parse(line).body[0]

    assert isinstance(import_from_ast, ast.ImportFrom)

    return ImportFrom.from_ast(import_from_ast)
