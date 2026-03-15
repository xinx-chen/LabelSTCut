import networkx as nx
from typing import Set, List, Dict, Tuple

class LabeledGraph:
    def __init__(self):
        self.G = nx.Graph()  # 无向图
        self.edge_labels = {}  # 存储边的标签：(u, v) → label（networkx边是无序的）

    def add_vertex(self, v: int):
        """添加顶点"""
        self.G.add_node(v)

    def add_edge(self, u: int, v: int, label: str):
        """添加带标签的边（无向边，u和v顺序无关）"""
        self.G.add_edge(u, v)
        # 用frozenset保证(u,v)和(v,u)对应同一个标签
        self.edge_labels[frozenset({u, v})] = label

    def remove_label_edges(self, label: str):
        """删除指定标签的所有边（返回删除的边，用于恢复）"""
        removed_edges = []
        for edge, lbl in self.edge_labels.items():
            if lbl == label:
                u, v = tuple(edge)
                removed_edges.append((u, v, lbl))
                self.G.remove_edge(u, v)
        return removed_edges

    def restore_edges(self, edges: List[Tuple[int, int, str]]):
        """恢复删除的边"""
        for u, v, lbl in edges:
            self.add_edge(u, v, lbl)

    def is_connected(self, s: int, t: int) -> bool:
        """判断s和t是否连通（用BFS）"""
        if s not in self.G.nodes or t not in self.G.nodes:
            return False
        return nx.has_path(self.G, s, t)

    def get_all_labels(self) -> Set[str]:
        """获取所有不同的标签"""
        return set(self.edge_labels.values())

    def get_vertex_count(self) -> int:
        """获取顶点数"""
        return self.G.number_of_nodes()

    def get_edge_count(self) -> int:
        """获取边数"""
        return self.G.number_of_edges()