from typing import Set

import pytest

from jig.visualizer.module_dependency.domain.model.graph import Graph
from jig.visualizer.module_dependency.domain.model.master_graph import MasterGraph
from jig.visualizer.module_dependency.domain.value.cluster import Cluster
from jig.visualizer.module_dependency.domain.value.module_edge import ModuleEdge
from jig.visualizer.module_dependency.domain.value.module_node import ModuleNode
from jig.visualizer.module_dependency.domain.value.module_path import ModulePath


def path(name: str) -> ModulePath:
    return ModulePath(name)


def node(name: str) -> ModuleNode:
    return ModuleNode.from_str(name)


def edge(tail: str, head: str) -> ModuleEdge:
    return ModuleEdge.from_str(tail, head)


def cluster(name: str, children: Set[str]) -> Cluster:
    return Cluster(
        module_path=path(name), children=set([node(name) for name in children])
    )


class TestGraph:
    def test_find_cluster(self):
        g = Graph()
        g.add_node(node("A"))
        g.add_node(node("B"))

        cluster_a = cluster("pkg_A", {"A"})
        cluster_b = cluster("pkg_B", {"B"})

        cluster_a.add_cluster(cluster_b)
        g.add_cluster(cluster_a)

        assert g.find_cluster(path("x")) is None
        assert g.find_cluster(path("pkg_A")) is cluster_a
        assert g.find_cluster(path("pkg_B")) is cluster_b

    def test_find_node_owner(self):
        g = Graph()
        g.add_node(node("A"))
        g.add_node(node("B"))

        child_cluster = cluster("pkg", {"B"})
        g.add_cluster(child_cluster)

        assert g.find_node_owner(node("foo")) is None
        assert g.find_node_owner(node("pkg")) is None
        assert g.find_node_owner(node("A")) is g
        assert g.find_node_owner(node("B")) is child_cluster

    def test_add_node(self):
        g = Graph()
        g.add_node(node("A"))

        expected = {"nodes": ["A"], "edges": [], "clusters": {}}

        assert g.to_dict() == expected

        g.add_node(node("A"))

        assert g.to_dict() == expected

    def test_add_edge(self):
        g = Graph()
        g.add_edge(edge("A", "B"))

        expected = {"nodes": ["A", "B"], "edges": [("A", "B")], "clusters": {}}

        assert g.to_dict() == expected

        g.add_edge(edge("A", "B"))

        assert g.to_dict() == expected

    def test_add_cluster(self):
        g = Graph()
        g.add_edge(edge("A", "B"))
        g.add_cluster(cluster("pkg", {"A", "B"}))

        assert g.to_dict() == {
            "nodes": ["A", "B"],
            "edges": [("A", "B")],
            "clusters": {"pkg": {"nodes": ["A", "B"], "clusters": {}}},
        }

        g.clusters[path("pkg")].add_cluster(cluster("pkg.child", {"C"}))
        assert g.to_dict() == {
            "nodes": ["A", "B"],
            "edges": [("A", "B")],
            "clusters": {
                "pkg": {
                    "nodes": ["A", "B"],
                    "clusters": {"pkg.child": {"clusters": {}, "nodes": ["C"]}},
                }
            },
        }

        # 親グラフが持っていないノードを含むクラスタが追加されたら、
        # 親グラフに含まれないノードを親グラフのノード管理に含める
        g.add_cluster(cluster("pkg_x", {"X"}))
        assert g.to_dict() == {
            "nodes": ["A", "B", "X"],
            "edges": [("A", "B")],
            "clusters": {
                "pkg": {
                    "nodes": ["A", "B"],
                    "clusters": {"pkg.child": {"clusters": {}, "nodes": ["C"]}},
                },
                "pkg_x": {"nodes": ["X"], "clusters": {}},
            },
        }

    def test_remove_node(self):
        g = Graph()
        g.add_edge(edge("A", "B"))

        assert g.to_dict() == {
            "nodes": ["A", "B"],
            "edges": [("A", "B")],
            "clusters": {},
        }

        g.remove_node(node("A"))

        assert g.to_dict() == {"nodes": ["B"], "edges": [], "clusters": {}}

    def test_remove_node_from_cluster(self):
        g = Graph()
        g.add_edge(edge("A", "B"))
        g.add_cluster(cluster("pkg", {"A"}))

        assert g.to_dict() == {
            "nodes": ["A", "B"],
            "edges": [("A", "B")],
            "clusters": {"pkg": {"nodes": ["A"], "clusters": {}}},
        }

        g.remove_node(node("A"))

        assert g.to_dict() == {
            "nodes": ["B"],
            "edges": [],
            "clusters": {},
        }

    def test_remove_cluster(self):
        # Graph所有のクラスタ削除
        g = Graph()
        g.add_edge(edge("A", "B"))
        g.add_cluster(cluster("pkg", {"A"}))

        assert g.to_dict() == {
            "nodes": ["A", "B"],
            "edges": [("A", "B")],
            "clusters": {"pkg": {"nodes": ["A"], "clusters": {}}},
        }

        g.remove_cluster(path("pkg"))

        assert g.to_dict() == {
            "nodes": ["B"],
            "edges": [],
            "clusters": {},
        }

        # 冪等なこと
        g.remove_cluster(path("pkg"))

        assert g.to_dict() == {
            "nodes": ["B"],
            "edges": [],
            "clusters": {},
        }

    def test_remove_cluster__parent_cluster(self):
        # 子を持つクラスタの削除
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
        g = Graph(master_graph=master_graph)
        g.dig(node("jig"))
        g.dig(node("jig.collector"))
        assert g.to_dict() == {
            "nodes": ["jig.cli", "jig.collector.application", "jig.collector.domain"],
            "edges": [
                ("jig.cli", "jig.collector.application"),
                ("jig.collector.application", "jig.collector.domain"),
            ],
            "clusters": {
                "jig": {
                    "clusters": {
                        "jig.collector": {
                            "nodes": [
                                "jig.collector.application",
                                "jig.collector.domain",
                            ],
                            "clusters": {},
                        }
                    },
                    "nodes": ["jig.cli"],
                },
            },
        }

        g.remove_cluster(path("jig"))
        assert g.to_dict() == {"nodes": [], "edges": [], "clusters": {}}

    def test_remove_cluster__child_cluster(self):
        # クラスタ内クラスタの削除
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
        g = Graph(master_graph=master_graph)
        g.dig(node("jig"))
        g.dig(node("jig.collector"))
        assert g.to_dict() == {
            "nodes": ["jig.cli", "jig.collector.application", "jig.collector.domain"],
            "edges": [
                ("jig.cli", "jig.collector.application"),
                ("jig.collector.application", "jig.collector.domain"),
            ],
            "clusters": {
                "jig": {
                    "clusters": {
                        "jig.collector": {
                            "nodes": [
                                "jig.collector.application",
                                "jig.collector.domain",
                            ],
                            "clusters": {},
                        }
                    },
                    "nodes": ["jig.cli"],
                },
            },
        }

        g.remove_cluster(path("jig.collector"))
        assert g.to_dict() == {
            "nodes": ["jig.cli"],
            "edges": [],
            "clusters": {"jig": {"clusters": {}, "nodes": ["jig.cli"]}},
        }

    def test_list_all_modules(self):
        g = Graph()
        g.add_edge(edge("A", "B"))

        cluster_a = cluster("pkg", {"A"})
        cluster_b = cluster("pkg.xxx", {"B"})

        cluster_a.add_cluster(cluster_b)
        g.add_cluster(cluster_a)

        assert g.list_all_modules() == [
            path("A"),
            path("B"),
            path("pkg"),
            path("pkg.xxx"),
        ]

    def test_list_all_nodes(self):
        g = Graph()
        g.add_edge(edge("A", "B"))
        g.add_edge(edge("A", "C"))

        cluster_a = cluster("pkg", {"A"})
        cluster_b = cluster("pkg.xxx", {"B"})

        cluster_a.add_cluster(cluster_b)
        g.add_cluster(cluster_a)

        assert g.list_all_nodes() == [
            node("A"),
            node("B"),
            node("C"),
        ]

    def test_is_removed_node(self):
        # クラスタ内クラスタの削除
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
        g = Graph(master_graph=master_graph)
        g.dig(node("jig"))
        g.dig(node("jig.collector"))
        assert g.to_dict() == {
            "nodes": ["jig.cli", "jig.collector.application", "jig.collector.domain"],
            "edges": [
                ("jig.cli", "jig.collector.application"),
                ("jig.collector.application", "jig.collector.domain"),
            ],
            "clusters": {
                "jig": {
                    "clusters": {
                        "jig.collector": {
                            "nodes": [
                                "jig.collector.application",
                                "jig.collector.domain",
                            ],
                            "clusters": {},
                        }
                    },
                    "nodes": ["jig.cli"],
                },
            },
        }

        assert g.is_removed_node(node("the.name.is.not.in.the.graph")) is False
        assert g.is_removed_node(node("jig")) is False
        assert g.is_removed_node(node("jig.cli")) is False
        assert g.is_removed_node(node("jig.collector")) is False
        assert g.is_removed_node(node("jig.collector.application")) is False
        assert g.is_removed_node(node("jig.collector.domain")) is False

        g.remove_node(node("jig.cli"))
        assert g.is_removed_node(node("jig.cli")) is True
        assert g.is_removed_node(node("jig")) is False

        g.remove_node(node("jig.collector.application"))
        assert g.is_removed_node(node("jig.collector.application")) is True
        assert g.is_removed_node(node("jig.collector")) is False

        g.remove_node(node("jig.collector.domain"))
        assert g.is_removed_node(node("jig.collector.domain")) is True
        assert g.is_removed_node(node("jig.collector")) is True
        assert g.is_removed_node(node("jig")) is True

    def test_focus(self):
        g = Graph()
        g.add_edge(edge("A", "B"))
        g.add_cluster(cluster("pkg", {"A"}))

        assert g.to_dict() == {
            "nodes": ["A", "B"],
            "edges": [("A", "B")],
            "clusters": {"pkg": {"nodes": ["A"], "clusters": {}}},
        }

        g.focus_nodes(node("B"))

        assert g.to_dict() == {
            "nodes": ["B"],
            "edges": [],
            "clusters": {},
        }

        # 冪等なこと
        g.focus_nodes(node("B"))

        assert g.to_dict() == {
            "nodes": ["B"],
            "edges": [],
            "clusters": {},
        }

    def test_focus__node_inside_a_package(self):
        g = Graph()
        g.add_edge(edge("A", "B"))
        g.add_cluster(cluster("pkg", {"A"}))

        assert g.to_dict() == {
            "nodes": ["A", "B"],
            "edges": [("A", "B")],
            "clusters": {"pkg": {"nodes": ["A"], "clusters": {}}},
        }

        g.focus_nodes(node("A"))

        assert g.to_dict() == {
            "nodes": ["A"],
            "edges": [],
            "clusters": {"pkg": {"nodes": ["A"], "clusters": {}}},
        }

    def test_focus__node_not_found(self):
        g = Graph()
        g.add_edge(edge("A", "B"))

        with pytest.raises(Exception):
            g.focus_nodes(node("C"))

    def test_focus__multiple_nodes(self):
        g = Graph()
        g.add_edge(edge("A", "B"))
        g.add_edge(edge("C", "D"))

        cluster_a = cluster("pkg_a", {"A"})
        cluster_b = cluster("pkg_b", {"B"})

        cluster_a.add_cluster(cluster_b)
        g.add_cluster(cluster_a)

        assert g.to_dict() == {
            "nodes": ["A", "B", "C", "D"],
            "edges": [("A", "B"), ("C", "D")],
            "clusters": {
                "pkg_a": {
                    "clusters": {"pkg_b": {"clusters": {}, "nodes": ["B"]}},
                    "nodes": ["A"],
                }
            },
        }

        g.focus_nodes(node("A"), node("C"))

        assert g.to_dict() == {
            "nodes": ["A", "C"],
            "edges": [],
            "clusters": {"pkg_a": {"clusters": {}, "nodes": ["A"]}},
        }

    def test_focus_nodes_and_clusters(self):
        g = Graph()
        g.add_edge(edge("A", "B"))
        g.add_edge(edge("C", "D"))

        cluster_a = cluster("pkg_a", {"A"})
        cluster_b = cluster("pkg_b", {"B"})

        cluster_a.add_cluster(cluster_b)
        g.add_cluster(cluster_a)

        assert g.to_dict() == {
            "nodes": ["A", "B", "C", "D"],
            "edges": [("A", "B"), ("C", "D")],
            "clusters": {
                "pkg_a": {
                    "clusters": {"pkg_b": {"clusters": {}, "nodes": ["B"]}},
                    "nodes": ["A"],
                }
            },
        }

        g.focus_nodes_and_clusters(node("pkg_b"), node("C"))

        assert g.to_dict() == {
            "nodes": ["B", "C"],
            "edges": [],
            "clusters": {
                "pkg_a": {
                    "clusters": {"pkg_b": {"clusters": {}, "nodes": ["B"]}},
                    "nodes": [],
                }
            },
        }

    def test_successors(self):
        g = Graph()
        g.add_edge(edge("A", "B"))

        assert g.successors(node("A")) == [node("B")]
        assert g.successors(node("B")) == []
        assert g.successors(node("C")) == []

    def test_predecessors(self):
        g = Graph()
        g.add_edge(edge("A", "B"))

        assert g.predecessors(node("A")) == []
        assert g.predecessors(node("B")) == [node("A")]
        assert g.predecessors(node("C")) == []

    def test_dig(self):
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
        g = Graph(master_graph=master_graph)

        assert g.to_dict() == {
            "nodes": ["jig"],
            "edges": [],
            "clusters": {},
        }

        g.dig(node("jig"))
        assert g.to_dict() == {
            "nodes": ["jig.cli", "jig.collector"],
            "edges": [("jig.cli", "jig.collector")],
            "clusters": {
                "jig": {"clusters": {}, "nodes": ["jig.cli", "jig.collector"]}
            },
        }

        g.dig(node("jig.collector"))
        assert g.to_dict() == {
            "nodes": ["jig.cli", "jig.collector.application", "jig.collector.domain"],
            "edges": [
                ("jig.cli", "jig.collector.application"),
                ("jig.collector.application", "jig.collector.domain"),
            ],
            "clusters": {
                "jig": {
                    "clusters": {
                        "jig.collector": {
                            "nodes": [
                                "jig.collector.application",
                                "jig.collector.domain",
                            ],
                            "clusters": {},
                        }
                    },
                    "nodes": ["jig.cli"],
                },
            },
        }

        g.dig(node("jig.collector.domain"))

        assert g.to_dict() == {
            "nodes": [
                "jig.cli",
                "jig.collector.application",
                "jig.collector.domain.source_code",
                "jig.collector.domain.source_file",
            ],
            "edges": [
                ("jig.cli", "jig.collector.application"),
                ("jig.collector.application", "jig.collector.domain.source_code"),
                ("jig.collector.application", "jig.collector.domain.source_file"),
                (
                    "jig.collector.domain.source_code",
                    "jig.collector.domain.source_file",
                ),
            ],
            "clusters": {
                "jig": {
                    "clusters": {
                        "jig.collector": {
                            "nodes": ["jig.collector.application"],
                            "clusters": {
                                "jig.collector.domain": {
                                    "nodes": [
                                        "jig.collector.domain.source_code",
                                        "jig.collector.domain.source_file",
                                    ],
                                    "clusters": {},
                                }
                            },
                        }
                    },
                    "nodes": ["jig.cli"],
                },
            },
        }

    def test_dig_complex(self):
        master_graph = MasterGraph.from_tuple_list(
            [
                ("jig.cli", "jig.analyzer"),
                ("jig.cli", "jig.visualizer.application"),
                ("jig.visualizer.application", "jig.analyzer"),
                ("jig.visualizer.application", "jig.visualizer.domain.edge"),
                ("jig.visualizer.application", "jig.visualizer.domain.node"),
                ("jig.visualizer.domain.edge", "jig.visualizer.domain.node"),
            ]
        )
        g = Graph(master_graph=master_graph)

        assert g.to_dict() == {
            "nodes": ["jig"],
            "edges": [],
            "clusters": {},
        }

        g.dig(node("jig"))

        assert g.to_dict() == {
            "nodes": ["jig.analyzer", "jig.cli", "jig.visualizer"],
            "edges": [
                ("jig.cli", "jig.analyzer"),
                ("jig.cli", "jig.visualizer"),
                ("jig.visualizer", "jig.analyzer"),
            ],
            "clusters": {
                "jig": {
                    "nodes": ["jig.analyzer", "jig.cli", "jig.visualizer"],
                    "clusters": {},
                }
            },
        }

        g.dig(node("jig.visualizer"))
        assert g.to_dict() == {
            "nodes": [
                "jig.analyzer",
                "jig.cli",
                "jig.visualizer.application",
                "jig.visualizer.domain",
            ],
            "edges": [
                ("jig.cli", "jig.analyzer"),
                ("jig.cli", "jig.visualizer.application"),
                ("jig.visualizer.application", "jig.analyzer"),
                ("jig.visualizer.application", "jig.visualizer.domain"),
            ],
            "clusters": {
                "jig": {
                    "nodes": ["jig.analyzer", "jig.cli"],
                    "clusters": {
                        "jig.visualizer": {
                            "nodes": [
                                "jig.visualizer.application",
                                "jig.visualizer.domain",
                            ],
                            "clusters": {},
                        },
                    },
                },
            },
        }

        g.dig(node("jig.visualizer.domain"))
        assert g.to_dict() == {
            "nodes": [
                "jig.analyzer",
                "jig.cli",
                "jig.visualizer.application",
                "jig.visualizer.domain.edge",
                "jig.visualizer.domain.node",
            ],
            "edges": [
                ("jig.cli", "jig.analyzer"),
                ("jig.cli", "jig.visualizer.application"),
                ("jig.visualizer.application", "jig.analyzer"),
                ("jig.visualizer.application", "jig.visualizer.domain.edge"),
                ("jig.visualizer.application", "jig.visualizer.domain.node"),
                ("jig.visualizer.domain.edge", "jig.visualizer.domain.node"),
            ],
            "clusters": {
                "jig": {
                    "nodes": ["jig.analyzer", "jig.cli"],
                    "clusters": {
                        "jig.visualizer": {
                            "nodes": ["jig.visualizer.application"],
                            "clusters": {
                                "jig.visualizer.domain": {
                                    "nodes": [
                                        "jig.visualizer.domain.edge",
                                        "jig.visualizer.domain.node",
                                    ],
                                    "clusters": {},
                                },
                            },
                        },
                    },
                },
            },
        }

    def test_dig_node_not_found(self):
        g = Graph()
        g.add_node(node("jig"))

        with pytest.raises(ValueError):
            g.dig(node("foo"))


class TestGraphScenario:
    """
    複数の操作を行うシナリオテスト
    """

    def test_remove_and_dig(self):
        """
        エッジの生えていないクラスタ内ノードが発生したとき、エラーにならずそのノードがGraphのnodesに追加されること
        """
        master_graph = MasterGraph.from_tuple_list(
            [
                ("tests.fixtures", "jig.visualizer"),
                ("tests.visualizer", "jig.visualizer"),
            ]
        )

        g = Graph(master_graph=master_graph)
        assert g.to_dict() == {
            "nodes": ["jig", "tests"],
            "edges": [("tests", "jig")],
            "clusters": {},
        }

        g.remove_node(node("jig"))
        assert g.to_dict() == {
            "nodes": ["tests"],
            "edges": [],
            "clusters": {},
        }

        g.dig(node("tests"))
        assert g.to_dict() == {
            "nodes": ["tests.fixtures", "tests.visualizer"],
            "edges": [],
            "clusters": {
                "tests": {
                    "nodes": ["tests.fixtures", "tests.visualizer"],
                    "clusters": {},
                }
            },
        }

    def test_remove_and_dig_inside_cluster(self):
        """
        エッジの生えていないノードがネストされたクラスタ内で発生したとき、そのノードがGraphのnodesに追加されること
        """
        master_graph = MasterGraph.from_tuple_list(
            [("tests.fixtures.download", "jig.visualizer")]
        )

        g = Graph(master_graph=master_graph)
        assert g.to_dict() == {
            "nodes": ["jig", "tests"],
            "edges": [("tests", "jig")],
            "clusters": {},
        }

        g.dig(node("tests"))
        assert g.to_dict() == {
            "nodes": ["jig", "tests.fixtures"],
            "edges": [("tests.fixtures", "jig")],
            "clusters": {"tests": {"nodes": ["tests.fixtures"], "clusters": {}}},
        }

        g.remove_node(node("jig"))
        assert g.to_dict() == {
            "nodes": ["tests.fixtures"],
            "edges": [],
            "clusters": {"tests": {"nodes": ["tests.fixtures"], "clusters": {}}},
        }

        g.dig(node("tests.fixtures"))
        assert g.to_dict() == {
            "nodes": ["tests.fixtures.download"],
            "edges": [],
            "clusters": {
                "tests": {
                    "nodes": [],
                    "clusters": {
                        "tests.fixtures": {
                            "nodes": ["tests.fixtures.download"],
                            "clusters": {},
                        }
                    },
                }
            },
        }
