import dataclasses


@dataclasses.dataclass(frozen=True)
class ModulePath:
    name: str

    def __post_init__(self):
        # not empty
        assert self.name

    @property
    def path_level(self) -> int:
        return len(self.name.split("."))

    def __lt__(self, other: "ModulePath"):
        return self.name < other.name

    def belongs_to(self, other: "ModulePath") -> bool:
        return self.name.startswith(other.name)

    def limit_path_level(self, max_path_level: int) -> "ModulePath":
        assert max_path_level > 0

        new_name = ".".join(self.name.split(".")[:max_path_level])
        return ModulePath(new_name)
