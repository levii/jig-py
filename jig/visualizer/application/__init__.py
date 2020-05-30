from typing import List

from jig.collector.domain import SourceCode


class DependencyTextVisualizer:
    def __init__(self, source_code: SourceCode, module_names: List[str]):
        self._source_code = source_code
        self._module_names= module_names

    def visualize(self) -> str:
        result = []
        for dep in self._source_code.module_dependencies(module_names=self._module_names):
            result.append(f"{dep[0]} -> {dep[1]}")

        return "\n".join(result)

