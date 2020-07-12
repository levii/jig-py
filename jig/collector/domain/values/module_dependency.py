import dataclasses

from jig.collector.domain.values.module_path import ModulePath


@dataclasses.dataclass(frozen=True)
class ModuleDependency:
    src: ModulePath
    dest: ModulePath
