import dataclasses
from typing import List, Optional

from jig.visualizer.module_dependency.domain.value.module_node_style import (
    ModuleNodeStyle,
)
from jig.visualizer.module_dependency.domain.value.module_path import ModulePath


@dataclasses.dataclass
class GraphStyle:
    node_styles: List[ModuleNodeStyle] = dataclasses.field(default_factory=list)

    def reset_all_styles(self):
        self.reset_node_styles()

    def reset_node_styles(self):
        self.node_styles.clear()

    def add_node_style(self, node_style: ModuleNodeStyle):
        # 同じモジュールパスへのスタイルは2つ追加させないが、適用順の整合性を合わせるため消してから後ろに追加する
        index = next(
            (
                i
                for i, v in enumerate(self.node_styles)
                if v.module_path == node_style.module_path
            ),
            None,
        )
        if index is not None:
            self.node_styles.pop(index)

        self.node_styles.append(node_style)

    def find_node_style(self, path: ModulePath) -> Optional[ModuleNodeStyle]:
        # 親のパスに対するスタイルも対象としてスタイルを取得する
        styles = [
            style for style in self.node_styles if path.belongs_to(style.module_path)
        ]

        if not styles:
            return None

        # 複数ある場合はpath_levelが大きい(=よりパスがマッチしている) ものを優先して返す
        return sorted(styles, reverse=True, key=lambda s: s.module_path.path_level)[0]
