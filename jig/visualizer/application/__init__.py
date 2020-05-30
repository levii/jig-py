from typing import List

from jig.collector.domain import SourceCode


class DependencyTextVisualizer:
    def __init__(self, source_codes: List[SourceCode], module_names: List[str]):
        self._source_codes = source_codes
        self._module_names = module_names

    def visualize(self) -> str:
        result = []
        for source_code in self._source_codes:
            result.append(f"---- {source_code.file.module_path}")
            for dep in source_code.module_dependencies(module_names=self._module_names):
                result.append(f"{dep[0]} -> {dep[1]}")

        return "\n".join(result)
