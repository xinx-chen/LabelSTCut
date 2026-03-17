import networkx as nx
from typing import List, Tuple, Set, Dict

class LabeledGraph:
    """带标签图的基础操作类，封装networkx的图操作，适配标签s-t割问题"""
    def __init__(self, n: int = 0):
        """
        初始化带标签图
        :param n: 顶点数（顶点编号从0开始）
        """
        self.G = nx.Graph()
        self.G.add_nodes_from(range(n))
        self.label_to_edges: Dict[int, List[Tuple[int, int]]] = {}  # label -> [(u,v), ...]
        self.edge_to_label: Dict[Tuple[int, int], int] = {}         # (u,v) -> label

    def add_edge(self, u: int, v: int, label: int) -> None:
        """添加带标签的边（自动处理u/v顺序，避免重复）"""
        if u < 0 or v < 0:
            raise ValueError(f"顶点编号不能为负数：u={u}, v={v}")
        # 统一边的存储顺序（u <= v），避免重复
        if u > v:
            u, v = v, u
        edge_key = (u, v)
        
        if edge_key not in self.edge_to_label:
            self.G.add_edge(u, v)
            self.edge_to_label[edge_key] = label
            if label not in self.label_to_edges:
                self.label_to_edges[label] = []
            self.label_to_edges[label].append(edge_key)

    def is_connected(self, s: int, t: int) -> bool:
        """判断s和t是否连通（处理顶点不存在的边界情况）"""
        if s == t:
            return True
        if s not in self.G.nodes() or t not in self.G.nodes():
            return False
        return nx.has_path(self.G, s, t)

    def remove_label(self, label: int) -> None:
        """移除指定标签的所有边"""
        if label not in self.label_to_edges:
            return
        # 遍历该标签的所有边并删除
        for edge_key in self.label_to_edges[label]:
            if self.G.has_edge(*edge_key):
                self.G.remove_edge(*edge_key)
                if edge_key in self.edge_to_label:
                    del self.edge_to_label[edge_key]
        del self.label_to_edges[label]

    def restore_label(self, original_graph: 'LabeledGraph', label: int) -> None:
        """从原始图恢复指定标签的所有边"""
        if label not in original_graph.label_to_edges:
            return
        for edge_key in original_graph.label_to_edges[label]:
            self.add_edge(*edge_key, label=label)

    def get_all_labels(self) -> Set[int]:
        """获取当前图的所有标签"""
        return set(self.label_to_edges.keys())

    def get_boundary_labels(self, s: int, original_edge_to_label: dict = None) -> Set[int]:
        """计算边界标签（修复顶点不存在的边界情况）"""
        if s not in self.G.nodes():
            return set()
        
        # 找到s所在的连通分量
        S = set(nx.node_connected_component(self.G, s))
        all_nodes = set(self.G.nodes())
        S_bar = all_nodes - S
        if not S_bar:
            return set()

        boundary_labels = set()
        # 优先使用原始图的边标签（论文要求）
        edge_label_map = original_edge_to_label if original_edge_to_label else self.edge_to_label
        for (u, v), label in edge_label_map.items():
            if (u in S and v in S_bar) or (u in S_bar and v in S):
                boundary_labels.add(label)
        return boundary_labels

    def copy(self) -> 'LabeledGraph':
        """深度拷贝（修复原浅拷贝导致的列表引用问题）"""
        new_graph = LabeledGraph()
        new_graph.G = self.G.copy()
        # 深度拷贝字典（包含列表的value）
        new_graph.label_to_edges = {k: v.copy() for k, v in self.label_to_edges.items()}
        new_graph.edge_to_label = self.edge_to_label.copy()
        return new_graph