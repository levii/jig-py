import os
import subprocess
import textwrap
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
                result.append(f"{dep.src} -> {dep.dest}")

        return "\n".join(result)


class DotTextVisualizer:
    def __init__(self, source_codes: List[SourceCode], module_names: List[str]):
        self._source_codes = source_codes
        self._module_names = module_names

    def visualize(self, depth: int) -> str:
        result = []
        for source_code in self._source_codes:
            for dep in source_code.module_dependencies(module_names=self._module_names):
                path1 = str(dep.src.path_in_depth(depth))
                path2 = str(dep.dest.path_in_depth(depth))

                # 自己参照は依存関係分析的には意味ないので除く
                if path1 == path2:
                    continue

                result.append(f'"{path1}" -> "{path2}";')

        # 重複削除とソート
        edges = sorted(list(set(result)))
        edge_text = "\n".join(edges)

        graph_text = ["digraph {", textwrap.indent(edge_text, "  "), "}"]

        return "\n".join(graph_text)


class DependencyImageVisualizer:
    def __init__(self, source_codes: List[SourceCode], module_names: List[str]):
        self._dot_text_visualizer = DotTextVisualizer(
            source_codes=source_codes, module_names=module_names
        )

    def visualize(self, depth: int, output_dir: str) -> None:
        dot = self._dot_text_visualizer.visualize(depth)

        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, f"dependency{depth}.png")

        p = subprocess.Popen(["dot", "-Tpng", f"-o{filepath}"], stdin=subprocess.PIPE)

        p.communicate(dot.encode())
