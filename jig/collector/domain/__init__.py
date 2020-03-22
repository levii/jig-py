import dataclasses
import os
from typing import List

from jig.collector.jig_ast import JigAST, ImportFrom


@dataclasses.dataclass(frozen=True)
class ModulePath:
    _path: str


@dataclasses.dataclass(frozen=True)
class ImportModule:
    module_path: ModulePath


@dataclasses.dataclass(frozen=True)
class ImportModuleCollection:
    _modules: List[ImportModule]

    def __len__(self) -> int:
        return len(self._modules)

    def __contains__(self, item: ImportModule):
        return item in self._modules

    # TODO: root_path, current_path をドメインオブジェクトにする
    @classmethod
    def build_by_import_from_ast(
        cls, root_path: str, current_path: str, import_from: ImportFrom
    ) -> "ImportModuleCollection":
        level = import_from.level if import_from.level is not None else 0
        prefix = cls._get_path_prefix(root_path, current_path, level)

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
    def _get_path_prefix(cls, root_path: str, current_path: str, level: int):
        if level < 1:
            return None

        relative_path = os.path.relpath(current_path, root_path)

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

    @classmethod
    def build(cls, source: SourceFile):
        return cls(_ast=JigAST.parse(source=source.content, filename=source.filename))

    def get_imports(self) -> ImportModuleCollection:
        imports = []
        for import_node in self._ast.imports():
            for name in import_node.names:
                imports.append(ImportModule(module_path=ModulePath(_path=name.name)))

        # TODO: ImportFromも取得してがっちゃんこする

        return ImportModuleCollection(imports)


@dataclasses.dataclass(frozen=True)
class SourceCode:
    file: SourceFile
    ast: SourceCodeAST
    import_modules: ImportModuleCollection


@dataclasses.dataclass(frozen=True)
class SourceCodeCollectRequest:
    file: SourceFile

    def build(self) -> SourceCode:
        ast = SourceCodeAST.build(self.file)
        return SourceCode(file=self.file, ast=ast, import_modules=ast.get_imports(),)
