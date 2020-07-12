from pathlib import Path

from jig.collector.domain.source_file.source_file import SourceFile
from jig.collector.domain.source_file.source_file_path import SourceFilePath


class TestSourceFile:
    def test_build(self):
        source_file = SourceFile(
            source_file_path=SourceFilePath(
                root_path=Path("/root"), file_path=Path("path/to/file.py")
            ),
            size=123,
            content="this is content",
        )
        assert isinstance(source_file, SourceFile)

        assert "this is content" not in repr(source_file)
        assert "this is content" not in str(source_file)
