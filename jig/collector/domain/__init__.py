import dataclasses
import os
from pathlib import Path
from typing import List, Optional

from jig.collector.domain.ast import ClassDef, JigSourceCode
from jig.collector.domain.ast import Import, ImportFrom
from jig.collector.domain.values.import_path import ImportPath


@dataclasses.dataclass(frozen=True)
class ModulePath:
    names: List[str]

    def __post_init__(self):
        if any([name.find(".") >= 0 for name in self.names]):
            raise ValueError(f"An invalid name specified in `{self.names}`")

    def __add__(self, other: "ModulePath") -> "ModulePath":
        return ModulePath(names=self.names + other.names)

    def join(self, name: str) -> "ModulePath":
        """
        パスを追加します
        :param name:
        :return:
        """
        return ModulePath(names=self.names + [name])

    @property
    def depth(self):
        return len(self.names)

    def path_in_depth(self, depth: int) -> "ModulePath":
        """
        このパスを指定されたdepthだけ辿ったパスを新たに返します
        :param depth:
        :return:
        """
        assert depth > 0
        return ModulePath(names=self.names[:depth])

    def belongs_to(self, other: "ModulePath") -> bool:
        """
        パスがotherに含まれているかどうかを返します。
        :param other:
        :return:
        """
        if self.depth < other.depth:
            return False

        return all([p1 == p2 for p1, p2 in zip(self.names, other.names)])

    def __str__(self) -> str:
        return ".".join(self.names)

    @classmethod
    def from_str(cls, path: str) -> "ModulePath":
        names = path.split(".")
        return cls(names=names)

    def match_module_names(self, module_names: List[str]) -> bool:
        return any(
            [self.match_module_name(module_name) for module_name in module_names]
        )

    def match_module_name(self, module_name: str) -> bool:
        path_str = str(self)
        return path_str == module_name or path_str.startswith(module_name + ".")


@dataclasses.dataclass(frozen=True)
class SourceFilePath:
    root_path: Path
    file_path: Path

    @property
    def module_path(self) -> ModulePath:
        relative_path = self.relative_path_from_root

        # root直下のファイルの場合、ファイル名がそのままモジュール名
        # そこからparentを辿ろうとするとパス表現が壊れる（"."になる）ため、root直下の場合は別で処理する
        if str(relative_path) == relative_path.name:
            return ModulePath(names=[relative_path.stem])

        # ディレクトリ配下の場合はパッケージファイル（__init__.py）の可能性もあるのでそれを考慮する
        dirname = relative_path.parent

        names = str(dirname).split(os.sep)
        if relative_path.stem != "__init__":
            names.append(relative_path.stem)

        return ModulePath(names=names)

    @property
    def filename(self) -> str:
        return self.file_path.name

    def module_path_with_level(self, level: int) -> ModulePath:
        """
        levelの数だけ上位に上ったパスを返します。
        :param level:
        :return:
        """
        assert level >= 1

        parent = self.relative_path_from_root.parents[level - 1]

        names = str(parent).split(os.sep)

        return ModulePath(names=names)

    def import_from_to_import_paths(self, import_from: ImportFrom) -> List[ImportPath]:
        """
        このソースファイルパスを基準にimport from を解決し、ModulePathのリストを返します。
        :param import_from:
        :return:
        """
        level = import_from.level if import_from.level is not None else 0

        if level < 1:
            assert import_from.module is not None

            p = ImportPath.from_str(import_from.module)
            return [p.join(alias.name) for alias in import_from.names]

        module_path = self.module_path_with_level(level)
        p = ImportPath.from_str(str(module_path))

        if import_from.module:
            p += ImportPath.from_str(import_from.module)

        return [p.join(alias.name) for alias in import_from.names]

    @property
    def relative_path_from_root(self) -> Path:
        # Path.relative_to は文字列化したパスから算出されるので絶対パスに揃えてから利用する
        root_path = self.root_path.absolute()
        file_path = self.file_path.absolute()

        return file_path.relative_to(root_path)

    @property
    def is_package(self):
        return self.file_path.stem == "__init__"


@dataclasses.dataclass(frozen=True)
class ImportModule:
    import_path: ImportPath


@dataclasses.dataclass(frozen=True)
class ImportPathCollection:
    _paths: List[ImportModule] = dataclasses.field(default_factory=list)

    def __len__(self) -> int:
        return len(self._paths)

    def __contains__(self, item: ImportModule):
        return item in self._paths

    def __add__(self, other: "ImportPathCollection") -> "ImportPathCollection":
        return ImportPathCollection(self._paths + other._paths)

    def __iter__(self):
        return self._paths.__iter__()

    @classmethod
    def build_by_import_ast(cls, import_ast: Import) -> "ImportPathCollection":
        imports = [
            ImportModule(import_path=ImportPath.from_str(name.name))
            for name in import_ast.names
        ]

        return ImportPathCollection(imports)

    @classmethod
    def build_by_import_from_ast(
        cls, file_path: SourceFilePath, import_from: ImportFrom
    ) -> "ImportPathCollection":

        imports = file_path.import_from_to_import_paths(import_from)
        return cls(
            _paths=[ImportModule(import_path=module_path) for module_path in imports]
        )


@dataclasses.dataclass(frozen=True)
class SourceFile:
    source_file_path: SourceFilePath
    size: int
    content: str = dataclasses.field(repr=False)

    @property
    def filename(self):
        return self.source_file_path.filename

    @property
    def module_path(self) -> ModulePath:
        return self.source_file_path.module_path


@dataclasses.dataclass(frozen=True)
class ModuleDependency:
    src: ModulePath
    dest: ModulePath


@dataclasses.dataclass(frozen=True)
class SourceCode:
    file: SourceFile
    import_paths: ImportPathCollection
    class_defs: List[ClassDef]

    @property
    def module_path(self) -> ModulePath:
        return self.file.module_path

    @classmethod
    def build(cls, file: SourceFile) -> "SourceCode":
        jig_source_code = JigSourceCode.build(
            source=file.content, filename=file.filename
        )

        return SourceCode(
            file=file,
            import_paths=cls._build_import_paths(file, jig_source_code),
            class_defs=jig_source_code.class_defs,
        )

    def module_dependencies(
        self, module_names: List[str] = None
    ) -> List[ModuleDependency]:
        if not module_names:
            return [
                ModuleDependency(
                    src=self.module_path,
                    dest=ModulePath.from_str(str(module.import_path)),
                )
                for module in self.import_paths
            ]

        dependencies = []
        for module in self.import_paths:
            if module.import_path.match_module_names(module_names):
                dependencies.append(
                    ModuleDependency(
                        src=self.module_path,
                        dest=ModulePath.from_str(str(module.import_path)),
                    )
                )

        return dependencies

    @classmethod
    def _build_import_paths(
        cls, file: SourceFile, jig_source_code: JigSourceCode
    ) -> ImportPathCollection:
        import_paths = ImportPathCollection()

        for import_ast in jig_source_code.imports:
            import_paths += ImportPathCollection.build_by_import_ast(import_ast)

        for import_from_ast in jig_source_code.import_froms:
            import_paths += ImportPathCollection.build_by_import_from_ast(
                file_path=file.source_file_path, import_from=import_from_ast
            )

        return import_paths


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
            source_file_path = source_code.file.source_file_path
            if str(source_file_path.relative_path_from_root) == relative_path:
                return source_code
        return None
