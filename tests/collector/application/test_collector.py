import os

from jig.collector.application import SourceCodeCollector


class TestSourceCodeCollector:
    root_path = os.environ["PYTEST_ROOT_DIR"]
    abspath = os.path.abspath(__file__)
    relative_path = abspath.replace(root_path + "/", "")

    def test_collect(self):
        collector = SourceCodeCollector(self.root_path)
