from jig.visualizer.module_dependency.domain.model.master_graph import MasterGraph
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode
from jig.visualizer.module_dependency.domain.value.module_node_adjacent import (
    ModuleNodeAdjacentGraph,
)
from jig.visualizer.module_dependency.domain.value.module_path import ModulePath


def node(name: str) -> ModuleNode:
    return ModuleNode.from_str(name)


def path(name: str) -> ModulePath:
    return ModulePath(name)


class TestMasterGraph:
    def test_has_module(self):
        master_graph = MasterGraph.from_tuple_list(
            [
                ("jig.collector.application", "jig.collector.domain.source_code"),
                ("jig.collector.application", "jig.collector.domain.source_file"),
                (
                    "jig.collector.domain.source_code",
                    "jig.collector.domain.source_file",
                ),
                ("jig.cli.main", "jig.collector.application"),
            ]
        )

        assert master_graph.has_module(path("jig")) is True
        assert master_graph.has_module(path("jig.cli")) is True
        assert master_graph.has_module(path("jig.cli.main")) is True
        assert master_graph.has_module(path("jig.collector.domain.source_file")) is True
        assert master_graph.has_module(path("jig.no_module")) is False

    def test_find_node_adjacent_graph(self):
        m = MasterGraph.from_tuple_list(
            [
                ("jig.collector.application", "jig.collector.domain.source_code"),
                ("jig.collector.application", "jig.collector.domain.source_file"),
                (
                    "jig.collector.domain.source_code",
                    "jig.collector.domain.source_file",
                ),
                ("jig.cli.main", "jig.collector.application"),
            ]
        )

        assert m.find_adjacent_graph(node("none")) is None

        assert m.find_adjacent_graph(node("jig")) == ModuleNodeAdjacentGraph(
            node=node("jig"),
            incoming_nodes=[],
            outgoing_nodes=[],
        )

        assert m.find_adjacent_graph(node("jig.cli")) == ModuleNodeAdjacentGraph(
            node=node("jig.cli"),
            incoming_nodes=[],
            outgoing_nodes=[node("jig.collector.application")],
        )

        assert m.find_adjacent_graph(node("jig.collector")) == ModuleNodeAdjacentGraph(
            node=node("jig.collector"),
            incoming_nodes=[node("jig.cli.main")],
            outgoing_nodes=[],
        )

        assert m.find_adjacent_graph(
            node("jig.collector.application")
        ) == ModuleNodeAdjacentGraph(
            node=node("jig.collector.application"),
            incoming_nodes=[node("jig.cli.main")],
            outgoing_nodes=[
                node("jig.collector.domain.source_code"),
                node("jig.collector.domain.source_file"),
            ],
        )
