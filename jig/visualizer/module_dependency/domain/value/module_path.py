import dataclasses
from typing import List


@dataclasses.dataclass(frozen=True)
class ModulePath:
    name: str

    def __post_init__(self):
        # not empty
        assert self.name

    @property
    def path_level(self) -> int:
        return len(self.parts)

    @property
    def parts(self) -> List[str]:
        return self.name.split(".")

    def __lt__(self, other: "ModulePath"):
        return self.name < other.name

    def belongs_to(self, other: "ModulePath") -> bool:
        if self.path_level < other.path_level:
            return False

        return all(map(lambda pair: pair[0] == pair[1], zip(self.parts, other.parts)))

    def limit_path_level(self, max_path_level: int) -> "ModulePath":
        assert max_path_level > 0

        new_name = ".".join(self.name.split(".")[:max_path_level])
        return ModulePath(new_name)

    def path_in_depth(self, depth: int) -> "ModulePath":
        """
        このパスを指定されたdepthだけ辿ったパスを新たに返します
        :param depth:
        :return:
        """
        assert depth > 0
        return ModulePath(".".join(self.parts[:depth]))
