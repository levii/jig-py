from jig.collector.domain import SourceCode, SourceFile, FilePath, SourceCodeCollection


class TestSourceCode:
    def test_build(self):
        root_path = "/path/to/something"
        main_py = SourceCode.build(
            file=SourceFile(
                path=FilePath(root_path=root_path, relative_path="main.py"),
                size=0,
                content="",
            )
        )
        test_py = SourceCode.build(
            file=SourceFile(
                path=FilePath(root_path=root_path, relative_path="test.py"),
                size=0,
                content="",
            )
        )
        assert isinstance(main_py, SourceCode)
        assert isinstance(test_py, SourceCode)

        collection = SourceCodeCollection([main_py, test_py])
        assert len(collection) == 2
        assert collection.get_by_relative_path("main.py") == main_py
        assert collection.get_by_relative_path("test.py") == test_py
