from typing import Optional

from jig.visualizer.module_dependency.domain.model.graph_style import GraphStyle
from jig.visualizer.module_dependency.domain.value.edge_style import EdgeStyle
from jig.visualizer.module_dependency.domain.value.module_edge_style import (
    ModuleEdgeStyle,
)
from jig.visualizer.module_dependency.domain.value.module_node_style import (
    ModuleNodeStyle,
)
from jig.visualizer.module_dependency.domain.value.module_path import ModulePath
from jig.visualizer.module_dependency.domain.value.node_style import NodeStyle
from jig.visualizer.module_dependency.domain.value.penwidth import Color


def path(path_str: str):
    return ModulePath(path_str)


def node_style(path_str: str, style: Optional[NodeStyle] = None):
    if not node_style:
        return ModuleNodeStyle(module_path=path(path_str))

    return ModuleNodeStyle(module_path=path(path_str), style=style)


def edge_style(tail: str, head: str, style: Optional[EdgeStyle] = None):
    if not node_style:
        return ModuleEdgeStyle(tail=path(tail), head=path(head))

    return ModuleEdgeStyle(
        tail=path(tail),
        head=path(head),
        style=style,
    )


class TestGraphStyle:
    def test_reset_all_styles(self):
        graph_style = GraphStyle()

        graph_style.add_node_style(node_style("jig"))
        graph_style.add_edge_style(edge_style("build", "jig"))

        graph_style.reset_all_styles()
        assert graph_style == GraphStyle()

    def test_add_node_style(self):
        graph_style = GraphStyle()

        assert len(graph_style.node_styles) == 0

        jig_style = node_style("jig", NodeStyle(color=Color.Blue))

        graph_style.add_node_style(jig_style)
        assert len(graph_style.node_styles) == 1

        tests_style = node_style("tests")
        graph_style.add_node_style(tests_style)

        assert len(graph_style.node_styles) == 2
        assert graph_style.node_styles == [jig_style, tests_style]

        jig_style2 = node_style("jig", NodeStyle(color=Color.Red))

        graph_style.add_node_style(jig_style2)
        assert len(graph_style.node_styles) == 2
        assert graph_style.node_styles == [tests_style, jig_style2]

    def test_add_edge_style(self):
        graph_style = GraphStyle()

        assert len(graph_style.edge_styles) == 0

        style1 = edge_style("tests", "jig", EdgeStyle(color=Color.Red))
        graph_style.add_edge_style(style1)
        assert len(graph_style.edge_styles) == 1

        style2 = edge_style("build", "jig", EdgeStyle(color=Color.Blue))
        graph_style.add_edge_style(style2)
        assert len(graph_style.edge_styles) == 2
        assert graph_style.edge_styles == [style1, style2]

        style3 = edge_style("tests", "jig", EdgeStyle(color=Color.Green))
        graph_style.add_edge_style(style3)
        assert len(graph_style.edge_styles) == 2
        assert graph_style.edge_styles == [style2, style3]

    def test_find_node_style(self):
        graph_style = GraphStyle()

        style = node_style("jig.collector", NodeStyle(color=Color.Blue))
        graph_style.add_node_style(style)

        assert graph_style.find_node_style(path("jig")) is None
        assert graph_style.find_node_style(path("jig.collector")) == style
        assert graph_style.find_node_style(path("jig.collector.domain")) == style

        # より詳細度の低いスタイルの適用
        jig_style = node_style("jig", NodeStyle(color=Color.Green))
        graph_style.add_node_style(jig_style)
        assert graph_style.find_node_style(path("jig")) == jig_style
        assert graph_style.find_node_style(path("jig.collector")) == style
        assert graph_style.find_node_style(path("jig.collector.domain")) == style

    def test_find_edge_style(self):
        gs = GraphStyle()

        style1 = edge_style("tests", "jig.collector", EdgeStyle(color=Color.Green))
        gs.add_edge_style(style1)

        assert gs.find_edge_style(path("tests"), path("jig")) is None
        assert gs.find_edge_style(path("tests"), path("jig.collector")) == style1
        assert gs.find_edge_style(path("tests"), path("jig.collector.domain")) == style1

        style2 = edge_style("tests", "jig", EdgeStyle(color=Color.Red))
        gs.add_edge_style(style2)

        assert gs.find_edge_style(path("tests"), path("jig")) == style2
        assert gs.find_edge_style(path("tests"), path("jig.collector")) == style1
        assert gs.find_edge_style(path("tests"), path("jig.collector.domain")) == style1
