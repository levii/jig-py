import dataclasses
from typing import List


@dataclasses.dataclass(frozen=True)
class ModulePath:
    names: List[str]

    def __post_init__(self):
        if any([name.find(".") >= 0 for name in self.names]):
            raise ValueError(f"An invalid name specified in `{self.names}`")
        if not self.names:
            raise ValueError("names must have least one element.")

    @classmethod
    def build(cls, names: List[str]) -> "ModulePath":
        return cls(names)

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

    def parent(self) -> "ModulePath":
        return self.build(names=self.names[:-1])

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
