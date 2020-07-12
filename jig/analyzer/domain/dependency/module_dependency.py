import dataclasses

from jig.collector.domain.values.module_path import ModulePath


@dataclasses.dataclass(frozen=True)
class ModuleDependency:
    src: ModulePath
    dest: ModulePath

    @classmethod
    def build(cls, src: ModulePath, dest: ModulePath) -> "ModuleDependency":
        return cls(src, dest)

    @classmethod
    def from_str(cls, src: str, dest: str) -> "ModuleDependency":
        return cls(src=ModulePath.from_str(src), dest=ModulePath.from_str(dest))
