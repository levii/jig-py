import dataclasses
from typing import List

from jig.analizer.domain import SourceCodeList
from jig.collector.domain import ModuleDependency


@dataclasses.dataclass(frozen=True)
class ModuleDependencyAnalyzer:
    source_code_list: SourceCodeList

    def analyze(self) -> List[ModuleDependency]:
        module_space = self.source_code_list.to_module_space()

        return [
            dep
            for dep in self.source_code_list.all_dependencies()
            if module_space.includes(dep.dest)
        ]
