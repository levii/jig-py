import dataclasses
import os
from typing import List, Tuple, Optional

from jig.collector.jig_ast import JigSourceCode
from jig.collector.jig_ast import ClassDef
from jig.collector.jig_ast import ImportFrom
from jig.collector.jig_ast import Import


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

    def match_module_names(self, module_names: List[str]) -> bool:
        return any(
            [self.match_module_name(module_name) for module_name in module_names]
        )

    def match_module_name(self, module_name: str) -> bool:
        return self.path == module_name or self.path.startswith(module_name + ".")


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

    def __iter__(self):
        return self._modules.__iter__()

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
class SourceCode:
    file: SourceFile
    module_path: ModulePath
    import_modules: ImportModuleCollection
    class_defs: List[ClassDef]

    @classmethod
    def build(cls, file: SourceFile) -> "SourceCode":
        jig_source_code = JigSourceCode.build(
            source=file.content, filename=file.filename
        )

        return SourceCode(
            file=file,
            module_path=ModulePath.build_by_file_path(path=file.path),
            import_modules=cls._build_import_modules(file, jig_source_code),
            class_defs=jig_source_code.class_defs,
        )

    def module_dependencies(self, module_names: List[str]) -> List[Tuple[str, str]]:
        if not module_names:
            return [
                (self.module_path.path, module.module_path.path)
                for module in self.import_modules
            ]

        dependencies = []
        for module in self.import_modules:
            if module.module_path.match_module_names(module_names):
                dependencies.append((self.module_path.path, module.module_path.path))

        return dependencies

    @classmethod
    def _build_import_modules(
        cls, file: SourceFile, jig_source_code: JigSourceCode
    ) -> ImportModuleCollection:
        import_modules = ImportModuleCollection()

        for import_ast in jig_source_code.imports:
            import_modules += ImportModuleCollection.build_by_import_ast(import_ast)

        for import_from_ast in jig_source_code.import_froms:
            import_modules += ImportModuleCollection.build_by_import_from_ast(
                file_path=file.path, import_from=import_from_ast
            )

        return import_modules


@dataclasses.dataclass(frozen=True)
class SourceCodeCollection:
    collection: List[SourceCode]

    def __iter__(self):
        return self.collection.__iter__()

    def __len__(self):
        return self.collection.__len__()

    def __getitem__(self, item):
        return self.collection.__getitem__(item)

    def get_by_relative_path(self, relative_path: str) -> Optional[SourceCode]:
        for source_code in self.collection:
            if source_code.file.path.relative_path == relative_path:
                return source_code
        return None
