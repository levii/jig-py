from jig.visualizer.module_dependency.domain.value.edge_style import EdgeStyle
from jig.visualizer.module_dependency.domain.value.module_edge import ModuleEdge
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode

from jig.visualizer.module_dependency.domain.model.hide_filter import HideFilter
from jig.visualizer.module_dependency.domain.value.node_style import NodeStyle


def node(path: str) -> ModuleNode:
    return ModuleNode.from_str(path)


def edge(tail: str, head: str) -> ModuleEdge:
    return ModuleEdge.from_str(tail, head)


class TestHideFilter:
    def test_reset(self):
        f = HideFilter()
        f.add_node(node("jig"))

        assert len(f.nodes) == 1

        f.reset()
        assert len(f.nodes) == 0

    def test_is_hidden_node(self):
        f = HideFilter()

        f.add_node(node("jig.collector"))

        assert f.is_hidden_node(node("xxx")) is False
        assert f.is_hidden_node(node("jig")) is False
        assert f.is_hidden_node(node("jig.collector")) is True
        assert f.is_hidden_node(node("jig.collector.domain")) is True

    def test_is_hidden_edge(self):
        f = HideFilter()

        f.add_node(node("jig.cli"))

        assert f.is_hidden_edge(edge("xxx", "yyy")) is False
        assert f.is_hidden_edge(edge("xxx", "jig")) is False
        assert f.is_hidden_edge(edge("xxx", "jig.cli")) is True
        assert f.is_hidden_edge(edge("xxx", "jig.cli.main")) is True
        assert f.is_hidden_edge(edge("jig", "xxx")) is False
        assert f.is_hidden_edge(edge("jig.cli", "xxx")) is True
        assert f.is_hidden_edge(edge("jig.cli.main", "xxx")) is True

    def test_filter_node_style(self):
        f = HideFilter()

        f.add_node(node("jig.cli"))

        current_style = NodeStyle(invisible=False)
        hidden_style = NodeStyle(invisible=True)

        assert f.filter_node_style(node("xxx"), current_style) == current_style
        assert f.filter_node_style(node("jig"), current_style) == current_style
        assert f.filter_node_style(node("jig.cli"), current_style) == hidden_style
        assert f.filter_node_style(node("jig.cli.main"), current_style) == hidden_style

    def test_filter_edge_style(self):
        f = HideFilter()

        f.add_node(node("jig.cli"))

        style = EdgeStyle(invisible=False)
        hidden_style = EdgeStyle(invisible=True)

        assert f.filter_edge_style(edge("xxx", "yyy"), style) == style
        assert f.filter_edge_style(edge("xxx", "yyy"), style) == style
        assert f.filter_edge_style(edge("xxx", "jig"), style) == style
        assert f.filter_edge_style(edge("xxx", "jig.cli"), style) == hidden_style
        assert f.filter_edge_style(edge("xxx", "jig.cli.main"), style) == hidden_style
        assert f.filter_edge_style(edge("jig", "xxx"), style) == style
        assert f.filter_edge_style(edge("jig.cli", "xxx"), style) == hidden_style
        assert f.filter_edge_style(edge("jig.cli.main", "xxx"), style) == hidden_style
