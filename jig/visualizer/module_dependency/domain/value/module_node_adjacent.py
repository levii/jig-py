import dataclasses
from typing import List

from .module_node import ModuleNode


@dataclasses.dataclass()
class ModuleNodeAdjacentGraph:
    node: ModuleNode
    incoming_nodes: List[ModuleNode]
    outgoing_nodes: List[ModuleNode]
