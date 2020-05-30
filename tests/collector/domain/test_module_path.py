from jig.collector.domain import FilePath, ModulePath


class TestModulePath:
    def test_build_by_file_path(self):
        path = FilePath(root_path="/root", relative_path="path/to/file.py")
        module_path = ModulePath.build_by_file_path(path)

        assert isinstance(module_path, ModulePath)
        assert module_path.path == "path.to.file"

    def test_build_by_file_path_init(self):
        path = FilePath(root_path="/root", relative_path="path/to/package/__init__.py")
        module_path = ModulePath.build_by_file_path(path)

        assert isinstance(module_path, ModulePath)
        assert module_path.path == "path.to.package"
