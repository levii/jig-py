from jig.visualizer.module_dependency.domain.model.master_graph import MasterGraph
from jig.visualizer.module_dependency.domain.value.module_path import ModulePath


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
