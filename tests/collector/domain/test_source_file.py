from jig.collector.domain import SourceFile


class TestSourceFile:
    def test_build(self):
        source_file = SourceFile(path="path/to/file.py", size=123, content="this is content")
        assert isinstance(source_file, SourceFile)

        assert "this is content" not in repr(source_file)
        assert "this is content" not in str(source_file)
