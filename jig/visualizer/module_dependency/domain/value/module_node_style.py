import dataclasses

from jig.visualizer.module_dependency.domain.value.module_path import ModulePath
from jig.visualizer.module_dependency.domain.value.node_style import NodeStyle


@dataclasses.dataclass(frozen=True)
class ModuleNodeStyle:
    module_path: ModulePath
    style: NodeStyle = dataclasses.field(default_factory=NodeStyle)
