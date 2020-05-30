import dataclasses
import os
from typing import List

from jig.collector.jig_ast import ClassDef
from jig.collector.jig_ast import JigAST, ImportFrom, Import


@dataclasses.dataclass(frozen=True)
class FilePath:
    root_path: str
    relative_path: str

    @property
    def abspath(self) -> str:
        return os.path.join(self.root_path, self.relative_path)

    @property
    def filename(self) -> str:
        return os.path.basename(self.relative_path)

    @property
    def basename(self) -> str:
        return os.path.splitext(self.filename)[0]

    @property
    def relative_dirname(self) -> str:
        return os.path.dirname(self.relative_path)

    @property
    def dirpath_list(self) -> List[str]:
        return self.relative_dirname.split(os.sep)

    def dirpath_list_with_relative_level(self, level: int) -> List[str]:
        """
        :param level:
        :return: level < 1 の時はから配列
        それ以外の場合は、level分パスを遡った時の相対ディレクトリのリストを返す
        """
        if level < 1:
            return []

        path_list = self.relative_path.split(os.sep)

        # level分遡ったパーツを結合する
        # return ".".join(path_list[:-level])
        return path_list[:-level]

    @classmethod
    def build_with_abspath(cls, root_path: str, abspath: str) -> "FilePath":
        return cls(
            root_path=root_path, relative_path=os.path.relpath(abspath, start=root_path)
        )


@dataclasses.dataclass(frozen=True)
class ModulePath:
    path: str

    @classmethod
    def build_by_file_path(cls, path: FilePath) -> "ModulePath":
        path_list = path.dirpath_list

        if path.filename != "__init__.py":
            path_list.append(path.basename)

        module_path = ".".join(path_list)

        return cls(module_path)


@dataclasses.dataclass(frozen=True)
class ImportModule:
    module_path: ModulePath


@dataclasses.dataclass(frozen=True)
class ImportModuleCollection:
    _modules: List[ImportModule] = dataclasses.field(default_factory=list)

    def __len__(self) -> int:
        return len(self._modules)

    def __contains__(self, item: ImportModule):
        return item in self._modules

    def __add__(self, other: "ImportModuleCollection") -> "ImportModuleCollection":
        return ImportModuleCollection(self._modules + other._modules)

    @classmethod
    def build_by_import_ast(cls, import_ast: Import) -> "ImportModuleCollection":
        imports = [
            ImportModule(module_path=ModulePath(path=name.name))
            for name in import_ast.names
        ]

        return ImportModuleCollection(imports)

    @classmethod
    def build_by_import_from_ast(
        cls, file_path: FilePath, import_from: ImportFrom
    ) -> "ImportModuleCollection":
        level = import_from.level if import_from.level is not None else 0

        imports = []
        for alias in import_from.names:
            # from xxx が.が含まれない場合、空配列
            path_list = file_path.dirpath_list_with_relative_level(level)

            # from句に名前指定がないときNone（from . や from .. など）
            # .fooなら"foo"が入る
            if import_from.module:
                path_list.append(import_from.module)

            if alias.name:
                path_list.append(alias.name)

            path = ModulePath(".".join(path_list))

            imports.append(ImportModule(path))

        return cls(_modules=imports)


@dataclasses.dataclass(frozen=True)
class SourceFile:
    path: FilePath
    size: int
    content: str = dataclasses.field(repr=False)

    @property
    def filename(self):
        return self.path.filename

    @property
    def module_path(self) -> ModulePath:
        return ModulePath.build_by_file_path(self.path)


@dataclasses.dataclass(frozen=True)
class SourceCodeAST:
    _ast: JigAST
    _source: SourceFile

    @classmethod
    def build(cls, source: SourceFile):
        return cls(
            _source=source,
            _ast=JigAST.parse(source=source.content, filename=source.filename),
        )

    def get_imports(self) -> ImportModuleCollection:
        import_modules = ImportModuleCollection()

        for import_ast in self._ast.imports():
            import_modules += ImportModuleCollection.build_by_import_ast(import_ast)

        for import_from_ast in self._ast.import_froms():
            import_modules += ImportModuleCollection.build_by_import_from_ast(
                file_path=self._source.path, import_from=import_from_ast
            )

        return import_modules

    def get_class_defs(self):
        return self._ast.class_defs()


@dataclasses.dataclass(frozen=True)
class SourceCode:
    file: SourceFile
    ast: SourceCodeAST
    import_modules: ImportModuleCollection
    class_defs: List[ClassDef]


@dataclasses.dataclass(frozen=True)
class SourceCodeCollectRequest:
    file: SourceFile

    def build(self) -> SourceCode:
        ast = SourceCodeAST.build(self.file)
        return SourceCode(
            file=self.file,
            ast=ast,
            import_modules=ast.get_imports(),
            class_defs=ast.get_class_defs(),
        )
