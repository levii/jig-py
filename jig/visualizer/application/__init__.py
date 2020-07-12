import os
import subprocess
import textwrap
from typing import List

from jig.analyzer.domain.dependency.module_dependency import ModuleDependency


class ModuleDependencyVisualizer:
    def __init__(self, dependencies: List[ModuleDependency]):
        self.dependencies = dependencies

    def dot_text(self, depth: int) -> str:
        result = []
        for dep in self.dependencies:
            path1 = str(dep.src.path_in_depth(depth))
            path2 = str(dep.dest.path_in_depth(depth))

            # 自己参照は依存関係分析的には意味ないので除く
            if path1 == path2:
                continue

            result.append(f'"{path1}" -> "{path2}";')

        # 設定テキスト
        setting_text = """
          graph [
            rankdir = "LR",
            overlap = "scale",
            ratio = "fill",
            fontsize = "24",
            fontname = "Helvetica",
            clusterrank = "local"
            dpi = 180
          ]

          node [
            fontsize=7
            shape=ellipse
          ];
        """

        # 重複削除とソート
        edges = sorted(list(set(result)))
        edge_text = "\n".join(edges)

        graph_text = [
            "digraph {",
            textwrap.indent(textwrap.dedent(setting_text), "  "),
            textwrap.indent(edge_text, "  "),
            "}",
        ]

        return "\n".join(graph_text)

    def render_dot_text(self, depth: int, output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, f"dependency{depth}.dot")

        with open(filepath, mode="w") as f:
            f.write(self.dot_text(depth))

    def visualize(self, depth: int, output_dir: str) -> None:
        dot = self.dot_text(depth)

        os.makedirs(output_dir, exist_ok=True)

        filepath = os.path.join(output_dir, f"dependency{depth}.png")

        p = subprocess.Popen(["dot", "-Tpng", f"-o{filepath}"], stdin=subprocess.PIPE)

        p.communicate(dot.encode())
