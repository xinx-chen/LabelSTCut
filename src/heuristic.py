import random
from collections import defaultdict
from src.graph import LabeledGraph
from typing import Set, Dict, List

def sample_msg(graph: LabeledGraph, s: int, t: int) -> Set[str]:
    """采样一个MSG（极小子图对应的标签集MSS）"""
    # 复制原图（避免修改原数据）
    import copy
    temp_graph = copy.deepcopy(graph)
    selected_labels = set()

    # 步骤1：随机选择标签，直到s和t连通
    while not temp_graph.is_connected(s, t):
        all_labels = list(temp_graph.get_all_labels())
        if not all_labels:
            break
        # 随机选一个标签添加
        lbl = random.choice(all_labels)
        selected_labels.add(lbl)
        # 恢复该标签的边
        for edge, edge_lbl in graph.edge_labels.items():
            if edge_lbl == lbl:
                u, v = tuple(edge)
                temp_graph.add_edge(u, v, lbl)

    # 步骤2：剔除冗余标签（核心：确保删除任一标签后s-t断开）
    redundant = []
    for lbl in selected_labels:
        # 临时删除该标签
        removed = temp_graph.remove_label_edges(lbl)
        if temp_graph.is_connected(s, t):
            # 冗余，保留删除状态
            redundant.append(lbl)
        else:
            # 非冗余，恢复标签
            temp_graph.restore_edges(removed)
    # 移除冗余标签
    for lbl in redundant:
        selected_labels.remove(lbl)
    return selected_labels

def monte_carlo_heuristic(
    graph: LabeledGraph,
    s: int,
    t: int,
    max_samples: int = 100  # 采样次数（论文建议100次）
) -> Set[str]:
    """蒙特卡洛启发式算法"""
    label_scores = defaultdict(int)

    # 步骤1：多次采样MSG，给标签打分
    for _ in range(max_samples):
        mss = sample_msg(graph, s, t)
        for lbl in mss:
            label_scores[lbl] += 1

    # 步骤2：按分数降序排序标签
    sorted_labels = sorted(label_scores.keys(), key=lambda x: label_scores[x], reverse=True)

    # 步骤3：依次选择标签，直到s-t断开（贪心选择）
    selected = set()
    temp_graph = copy.deepcopy(graph)
    for lbl in sorted_labels:
        selected.add(lbl)
        # 删除该标签的边
        temp_graph.remove_label_edges(lbl)
        if not temp_graph.is_connected(s, t):
            break

    # 步骤4：冗余剔除（优化结果）
    final_selected = selected.copy()
    for lbl in selected:
        final_selected.remove(lbl)
        # 临时恢复其他标签的边，只删除final_selected的标签
        test_graph = copy.deepcopy(graph)
        for l in final_selected:
            test_graph.remove_label_edges(l)
        if not test_graph.is_connected(s, t):
            # 该标签冗余，永久删除
            continue
        else:
            # 非冗余，恢复
            final_selected.add(lbl)
    return final_selected

if __name__ == "__main__":
    # 测试算法
    from src.utils import load_graph_from_json
    graph, s, t = load_graph_from_json("data/small/instance_1.json")
    heuristic_cut = monte_carlo_heuristic(graph, s, t)
    print(f"启发式算法找到的标签割：{heuristic_cut}，大小：{len(heuristic_cut)}")