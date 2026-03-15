import math
import copy
from src.graph import LabeledGraph
from typing import Set, List

def zft18_approx_algorithm(graph: LabeledGraph, s: int, t: int) -> Set[str]:
    """ZFT18近似算法（两阶段策略）"""
    temp_graph = copy.deepcopy(graph)
    stage1_labels = set()
    n = temp_graph.get_vertex_count()

    # 步骤1：猜测OPT（用标签总数的平方根近似，简化实现）
    all_labels = temp_graph.get_all_labels()
    guess_opt = int(math.sqrt(len(all_labels))) if all_labels else 1
    threshold = int(n ** (2/3) / (guess_opt ** (1/3)))  # 路径长度阈值

    # 阶段1：反复删除短路径对应的标签
    while True:
        # 找最短s-t路径
        try:
            shortest_path = nx.shortest_path(temp_graph.G, s, t)
        except nx.NetworkXNoPath:
            break  # 已断开
        if len(shortest_path) - 1 > threshold:  # 路径长度=边数=节点数-1
            break
        # 收集路径上的所有标签
        path_labels = set()
        for i in range(len(shortest_path)-1):
            u = shortest_path[i]
            v = shortest_path[i+1]
            lbl = temp_graph.edge_labels[frozenset({u, v})]
            path_labels.add(lbl)
        # 添加到阶段1标签集，删除这些标签的边
        stage1_labels.update(path_labels)
        for lbl in path_labels:
            temp_graph.remove_label_edges(lbl)

    # 阶段2：找剩余图的最小边割，收集对应标签
    stage2_labels = set()
    if temp_graph.is_connected(s, t):
        # 用networkx的最小割函数（返回边割集）
        edge_cut = nx.minimum_edge_cut(temp_graph.G, s, t)
        for u, v in edge_cut:
            lbl = temp_graph.edge_labels[frozenset({u, v})]
            stage2_labels.add(lbl)

    # 合并两阶段标签，冗余剔除
    final_labels = stage1_labels.union(stage2_labels)
    # 冗余剔除（和启发式算法一致）
    redundant = []
    for lbl in final_labels:
        final_labels.remove(lbl)
        test_graph = copy.deepcopy(graph)
        for l in final_labels:
            test_graph.remove_label_edges(l)
        if not test_graph.is_connected(s, t):
            redundant.append(lbl)
        else:
            final_labels.add(lbl)
    for lbl in redundant:
        final_labels.discard(lbl)
    return final_labels