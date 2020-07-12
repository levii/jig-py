import dataclasses
from typing import List


@dataclasses.dataclass(frozen=True)
class ImportPath:
    names: List[str]

    def __post_init__(self):
        if any([name.find(".") >= 0 for name in self.names]):
            raise ValueError(f"An invalid name specified in `{self.names}`")

    def __add__(self, other: "ImportPath") -> "ImportPath":
        return ImportPath(names=self.names + other.names)

    def join(self, name: str) -> "ImportPath":
        """
        パスを追加します
        :param name:
        :return:
        """
        return ImportPath(names=self.names + [name])

    @property
    def depth(self):
        return len(self.names)

    def path_in_depth(self, depth: int) -> "ImportPath":
        """
        このパスを指定されたdepthだけ辿ったパスを新たに返します
        :param depth:
        :return:
        """
        assert depth > 0
        return ImportPath(names=self.names[:depth])

    def belongs_to(self, other: "ImportPath") -> bool:
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
    def from_str(cls, path: str) -> "ImportPath":
        names = path.split(".")
        return cls(names=names)

    def match_module_names(self, module_names: List[str]) -> bool:
        return any(
            [self.match_module_name(module_name) for module_name in module_names]
        )

    def match_module_name(self, module_name: str) -> bool:
        path_str = str(self)
        return path_str == module_name or path_str.startswith(module_name + ".")
