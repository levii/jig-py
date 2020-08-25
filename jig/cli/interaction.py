import dataclasses

from jig.analyzer.domain.dependency.import_dependency import ImportDependencyCollection
from jig.cli.main import _collect_source_codes
from jig.visualizer.module_dependency.domain.model.graph import Graph
from jig.visualizer.module_dependency.domain.model.master_graph import MasterGraph
from jig.visualizer.module_dependency.presentation.controller.graph_controller import (
    GraphController,
)


@dataclasses.dataclass
class Jig:
    @classmethod
    def analyze_module_dependency(cls, project_root_path: str) -> GraphController:
        source_codes = _collect_source_codes(project_root_path=project_root_path)

        collection = ImportDependencyCollection.build_from_source_code_collection(
            source_codes
        )
        dependencies = collection.build_module_dependencies()
        dependency_tuples = []
        for dependency in dependencies:
            dependency_tuples.append((str(dependency.src), str(dependency.dest)))

        master_graph = MasterGraph.from_tuple_list(dependency_tuples)
        graph = Graph(master_graph=master_graph)

        return GraphController(graph=graph)
