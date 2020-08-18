import dataclasses
from typing import Set

from jig.visualizer.module_dependency.domain.value.module_edge import ModuleEdge


@dataclasses.dataclass
class MasterGraph:
    edges: Set[ModuleEdge] = dataclasses.field(default_factory=set)
