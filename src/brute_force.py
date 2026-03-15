from itertools import combinations
from src.graph import LabeledGraph
from typing import Set

def brute_force_min_label_cut(graph: LabeledGraph, s: int, t: int) -> Set[str]:
    """枚举法求最优标签割（仅适用于标签数少的小规模实例）"""
    all_labels = list(graph.get_all_labels())
    n_labels = len(all_labels)

    # 从标签数1开始枚举，找到最小的可行割
    for k in range(1, n_labels + 1):
        # 枚举所有k个标签的组合
        for candidate in combinations(all_labels, k):
            candidate_set = set(candidate)
            # 临时删除这些标签的边
            removed_edges = []
            for lbl in candidate_set:
                removed = graph.remove_label_edges(lbl)
                removed_edges.extend(removed)
            # 判断s和t是否断开
            if not graph.is_connected(s, t):
                # 恢复边并返回最优解
                graph.restore_edges(removed_edges)
                return candidate_set
            # 恢复边
            graph.restore_edges(removed_edges)
    # 所有标签都删了（极端情况）
    return set(all_labels)