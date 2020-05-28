import dataclasses
import os
from typing import List

from jig.collector.jig_ast import JigAST, ImportFrom, Import


@dataclasses.dataclass(frozen=True)
class ModulePath:
    _path: str


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
            ImportModule(module_path=ModulePath(_path=name.name))
            for name in import_ast.names
        ]

        return ImportModuleCollection(imports)

    @classmethod
    def build_by_import_from_ast(
        cls, root_path: str, file_path: str, import_from: ImportFrom
    ) -> "ImportModuleCollection":
        level = import_from.level if import_from.level is not None else 0
        prefix = cls._get_path_prefix(root_path, file_path, level)

        imports = []
        for alias in import_from.names:
            # prefixもimport_from.moduleも存在しない（None）なことがあるのでフィルタする
            # prefix: from xxx が相対パス指定じゃない場合None
            # import_from.module: from句に名前指定がないときNone（from . や from .. など）
            path_list = list(
                filter(lambda x: x, [prefix, import_from.module, alias.name])
            )

            path = ModulePath(".".join(path_list))

            imports.append(ImportModule(path))

        return cls(_modules=imports)

    @classmethod
    def _get_path_prefix(cls, root_path: str, file_path: str, level: int):
        if level < 1:
            return None

        relative_path = os.path.relpath(file_path, root_path)

        path_list = relative_path.split(os.sep)

        # level分遡ったパーツを結合する
        return ".".join(path_list[:-level])


@dataclasses.dataclass(frozen=True)
class SourceFile:
    path: str
    content: str
    size: int

    @property
    def filename(self):
        return os.path.basename(self.path)


@dataclasses.dataclass(frozen=True)
class SourceCodeAST:
    _ast: JigAST
    _source: SourceFile
    _root_path: str

    @classmethod
    def build(cls, root_path: str, source: SourceFile):
        return cls(
            _root_path=root_path,
            _source=source,
            _ast=JigAST.parse(source=source.content, filename=source.filename),
        )

    def get_imports(self) -> ImportModuleCollection:
        import_modules = ImportModuleCollection()

        for import_ast in self._ast.imports():
            import_modules += ImportModuleCollection.build_by_import_ast(import_ast)

        for import_from_ast in self._ast.import_froms():
            import_modules += ImportModuleCollection.build_by_import_from_ast(
                self._root_path, self._source.path, import_from_ast
            )

        return import_modules

    def get_class_defs(self):
        return self._ast.class_defs()


@dataclasses.dataclass(frozen=True)
class SourceCode:
    file: SourceFile
    ast: SourceCodeAST
    import_modules: ImportModuleCollection


@dataclasses.dataclass(frozen=True)
class SourceCodeCollectRequest:
    root_path: str
    file: SourceFile

    def build(self) -> SourceCode:
        ast = SourceCodeAST.build(self.root_path, self.file)
        return SourceCode(file=self.file, ast=ast, import_modules=ast.get_imports(),)
