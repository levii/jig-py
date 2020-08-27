import dataclasses
from typing import Set, List, Dict, Optional, Union

from jig.visualizer.module_dependency.domain.model.master_graph import MasterGraph
from jig.visualizer.module_dependency.domain.value.cluster import Cluster
from jig.visualizer.module_dependency.domain.value.module_edge import (
    ModuleEdge,
    ModuleEdgeCollection,
    ModuleEdgeStyle,
)
from jig.visualizer.module_dependency.domain.value.module_node import (
    ModuleNode,
    ModuleNodeStyle,
)
from jig.visualizer.module_dependency.domain.value.penwidth import Color, PenWidth


class NodeNotFoundError(Exception):
    pass


@dataclasses.dataclass
class Graph:
    master_graph: MasterGraph = dataclasses.field(default_factory=MasterGraph)
    nodes: Set[ModuleNode] = dataclasses.field(default_factory=set)
    edges: Set[ModuleEdge] = dataclasses.field(default_factory=set)
    clusters: Dict[ModuleNode, Cluster] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        self.reset()

    def reset(self) -> None:
        self.nodes.clear()
        self.edges.clear()
        self.clusters.clear()

        # トップレベルの依存関係をGraphに追加する
        for edge in self.master_graph.edges:
            tail = edge.tail.path_in_depth(1).name
            head = edge.head.path_in_depth(1).name
            if tail == head:
                self.add_node(ModuleNode.from_str(tail))
            else:
                self.add_edge(ModuleEdge.from_str(tail=tail, head=head))

    def to_dict(self) -> dict:
        nodes = sorted([n.name for n in self.nodes])
        edges = sorted([(e.tail.name, e.head.name) for e in self.edges])
        clusters = dict(
            [(node.name, cluster.to_dict()) for node, cluster in self.clusters.items()]
        )

        return {"nodes": nodes, "edges": edges, "clusters": clusters}

    def find_cluster(self, node: ModuleNode) -> Optional[Cluster]:
        for cluster in self.clusters.values():
            if cluster.node == node:
                return cluster

            sub_cluster = cluster.find_cluster(node)
            if sub_cluster:
                return sub_cluster

        return None

    def find_node_owner(self, node: ModuleNode) -> Optional[Union["Graph", Cluster]]:
        for cluster in self.clusters.values():
            owner = cluster.find_node_owner(node)
            if owner:
                return owner

        if node in self.nodes:
            return self

        return None

    def add_node(self, node: ModuleNode):
        self.nodes.add(node)

    def add_edge(self, edge: ModuleEdge):
        if edge.is_self_loop():
            return

        self.edges.add(edge)

        self.add_node(edge.tail)
        self.add_node(edge.head)

    def add_cluster(self, cluster: Cluster):
        not_included = cluster.children - self.nodes

        # 親グラフが全てのノード情報を持つ前提条件を守るため、
        # 親グラフに含まれないノードを親グラフのノード管理に含める
        for node in not_included:
            self.add_node(node)

        self.clusters[cluster.node] = cluster

    def has_cluster(self, node: ModuleNode) -> bool:
        if node in self.clusters:
            return True

        for cluster in self.clusters.values():
            if cluster.has_cluster(node):
                return True

        return False

    def remove_node(self, node: ModuleNode):
        if node in self.nodes:
            self.nodes.remove(node)

        edges = list(filter(lambda e: e.has_node(node), self.edges))
        for edge in edges:
            self.edges.remove(edge)

        self._remove_node_from_cluster(node)

    def _remove_node_from_cluster(self, node: ModuleNode):
        # Dict#values() で for を回しているときには、要素削除できないので、 List にキャストする
        for cluster in list(self.clusters.values()):
            cluster.remove(node)

            if cluster.is_empty:
                del self.clusters[cluster.node]

    def remove_cluster(self, node: ModuleNode):
        cluster = self.find_cluster(node)
        if not cluster:
            return

        for node in cluster.descendant_nodes():
            self.remove_node(node)

    def focus_nodes(self, node: ModuleNode, *extra_nodes: ModuleNode):
        """
        指定されたノードのみをグラフに残す。
        :param node: 残したいノード
        :param extra_nodes: 追加で残したいノード
        :return:
        """
        focus_nodes = {node, *extra_nodes}

        for focus_node in focus_nodes:
            if focus_node not in self.nodes:
                raise NodeNotFoundError(f"Graphに含まれないノードが指定されました: {focus_node}")

        for current_node in list(self.nodes):
            if current_node not in focus_nodes:
                self.remove_node(current_node)

    def focus_nodes_and_clusters(self, node: ModuleNode, *extra_nodes: ModuleNode):
        """
        指定されたノードおよびクラスタのみをグラフに残す。
        :param node: 残したいノードおよびクラスタ
        :param extra_nodes: 追加で残したいノードおよびクラスタ
        :return:
        """
        input_nodes = {node, *extra_nodes}
        focus_nodes = set()

        for node in input_nodes:
            cluster = self.find_cluster(node)
            if cluster:
                focus_nodes |= set(cluster.descendant_nodes())
                continue

            if node in self.nodes:
                focus_nodes.add(node)

        if len(focus_nodes) == 0:
            # 残すノードが見つからなかった場合はフォーカスできないので何もしない
            return

        self.focus_nodes(focus_nodes.pop(), *focus_nodes)

    def child_node_exists(self, node: ModuleNode) -> bool:
        return self.master_graph.child_node_exists(node)

    def hide_node(self, node: ModuleNode):
        if node in self.nodes:
            self.nodes.remove(node)
            self.nodes.add(node.to_invisible())

        edges = list(filter(lambda e: e.has_node(node), self.edges))
        for edge in edges:
            self.edges.remove(edge)
            self.edges.add(edge.to_invisible())

        for cluster in self.clusters.values():
            cluster.hide_node(node)

    def style(
        self, node: ModuleNode, color: Color, fontcolor: Color, penwidth: PenWidth
    ):
        node_style = ModuleNodeStyle(
            color=color, fontcolor=fontcolor, penwidth=penwidth
        )
        edge_style = ModuleEdgeStyle(
            color=color, fontcolor=fontcolor, penwidth=penwidth
        )

        if node in self.nodes:
            self.nodes.remove(node)
            self.nodes.add(node.with_style(style=node_style))

        edges = list(filter(lambda e: e.has_node(node), self.edges))
        for edge in edges:
            self.edges.remove(edge)
            self.edges.add(edge.with_style(style=edge_style))

    def edge_style(
        self, tail: ModuleNode, head: ModuleNode, color: Color, penwidth: PenWidth
    ):
        edge_style = ModuleEdgeStyle(color=color, penwidth=penwidth)
        e = ModuleEdge(tail=tail, head=head)

        edges = [
            edge.with_style(edge_style) if edge.belongs_to(e) else edge
            for edge in self.edges
        ]
        self.edges.clear()
        self.edges.update(edges)

    def reset_style(self) -> None:
        nodes = [node.reset_style() for node in self.nodes]
        self.nodes.clear()
        self.nodes.update(nodes)

        edges = [edge.reset_style() for edge in self.edges]
        self.edges.clear()
        self.edges.update(edges)

    def auto_highlight(self):
        source_nodes: Dict[ModuleNode, List[ModuleEdge]] = dict(
            [(node, []) for node in self.nodes]
        )
        dest_nodes: Dict[ModuleNode, List[ModuleEdge]] = dict(
            [(node, []) for node in self.nodes]
        )
        for edge in self.edges:
            source_nodes[edge.tail].append(edge)
            dest_nodes[edge.head].append(edge)

        # entrypoint
        entrypoint_node_style = ModuleNodeStyle(
            color=Color.Purple, fontcolor=Color.White, filled=True
        )
        for node, edges in source_nodes.items():
            if len(edges) == 0:
                self.nodes.remove(node)
                self.nodes.add(node.with_style(style=entrypoint_node_style))

        # fundamental
        fundamental_node_style = ModuleNodeStyle(
            color=Color.Teal, fontcolor=Color.White, filled=True
        )
        for node, edges in dest_nodes.items():
            if len(edges) == 0:
                self.nodes.remove(node)
                self.nodes.add(node.with_style(style=fundamental_node_style))

        # both reference
        both_reference_edge_style = ModuleEdgeStyle(
            color=Color.Red, penwidth=PenWidth.Bold
        )
        for edge in self.edges:
            reverse = edge.build_reverse()
            if reverse in self.edges:
                self.edges.remove(edge)
                self.edges.add(edge.with_style(style=both_reference_edge_style))

    def successors(self, node: ModuleNode) -> List[ModuleNode]:
        return [e.head for e in self.edges if e.tail == node]

    def predecessors(self, node: ModuleNode) -> List[ModuleNode]:
        return [e.tail for e in self.edges if e.head == node]

    def dig(self, node: ModuleNode):
        if self.has_cluster(node):
            # 既にクラスタ化されているので、処理をスキップする
            return

        if not self.child_node_exists(node):
            # dig できない (指定した node の配下に位置する node が存在しない)
            raise ValueError(f"指定されたモジュール {node.name} の配下に位置するノードがありません (digできません)")

        node_owner = self.find_node_owner(node)
        if not node_owner:
            raise ValueError(f"指定されたモジュール {node.name} が存在しません。")

        next_path_level = node.path_level + 1

        self._dig_successors(node, next_path_level)
        self._dig_predecessors(node, next_path_level)
        self._dig_inner_edge(node, next_path_level)
        self._dig_clustering(node, next_path_level, node_owner)

        self.remove_node(node)

    def _dig_inner_edge(self, node: ModuleNode, next_path_level: int):
        for edge in self.master_graph.find_edges(node):
            self.add_edge(edge.limit_path_level(next_path_level))

    def _dig_clustering(
        self,
        node: ModuleNode,
        next_path_level: int,
        node_owner: Union["Graph", Cluster],
    ):
        cluster = Cluster(node=node)
        for n in self.master_graph.find_nodes(node):
            new_node = n.limit_path_level(next_path_level)
            cluster.add(new_node)
            self.add_node(new_node)

        node_owner.add_cluster(cluster)

    def _dig_successors(self, node: ModuleNode, next_path_level: int):
        # 現在のnodeからの接続先エッジを取得
        current_edges = ModuleEdgeCollection(
            [ModuleEdge(node, s) for s in self.successors(node)]
        )

        for new_edge in self.master_graph:
            parent_edge = current_edges.find_parent_edge(new_edge)

            if parent_edge:
                # ノード分解した新しいノードから、ノード分解していないノードへつなぐ
                edge = ModuleEdge(
                    new_edge.tail.limit_path_level(next_path_level), parent_edge.head
                )
                self.add_edge(edge)

    def _dig_predecessors(self, node: ModuleNode, next_path_level: int):
        # 現在のnodeからの接続元エッジを取得
        current_edges = ModuleEdgeCollection(
            [ModuleEdge(p, node) for p in self.predecessors(node)]
        )

        for new_edge in self.master_graph:
            parent_edge = current_edges.find_parent_edge(new_edge)

            if parent_edge:
                # ノード分解した新しいノードから、ノード分解していないノードへつなぐ
                edge = ModuleEdge(
                    parent_edge.tail, new_edge.head.limit_path_level(next_path_level)
                )
                self.add_edge(edge)
