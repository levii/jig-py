import dataclasses
import os
from pathlib import Path
from typing import List

from jig.collector.domain.ast import ImportFrom
from jig.collector.domain.values.import_path import ImportPath
from jig.collector.domain.values.module_path import ModulePath


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

    @property
    def can_convert_to_module_path(self) -> bool:
        """
        パスがモジュールパスとして扱えるかどうかを返す。
        :return:
        """
        # ディレクトリパスをチェック
        dir_path = str(self.relative_path_from_root.parent)
        if dir_path != "." and dir_path.find(".") >= 0:
            return False

        # ファイル名の拡張子を外してチェック
        name = self.relative_path_from_root.stem
        return name.find(".") < 0
