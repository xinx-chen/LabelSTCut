from src.graph_base import LabeledGraph
from src.utils import remove_redundant_labels
from typing import Set
import random

def sample_mss(original_graph: LabeledGraph, s: int, t: int, random_seed: int = None) -> Set[int]:
    """
    Algorithm3：随机删标签的MSS采样
    :param original_graph: 原始图（未修改的带标签图）
    :param s: 源点
    :param t: 汇点
    :param random_seed: 随机种子（None则使用全局种子）
    :return: MSS标签集M
    """
    if random_seed is not None:
        random.seed(random_seed)
    
    # 边界检查
    if s not in original_graph.G.nodes() or t not in original_graph.G.nodes():
        raise ValueError(f"源点s={s}或汇点t={t}不在图中")
    if not original_graph.is_connected(s, t):
        raise ValueError(f"原始图中s={s}和t={t}已断连，无法采样MSS")

    # 步骤1：复制原图，初始化标签集
    mss_graph = original_graph.copy()
    all_labels = set(mss_graph.get_all_labels())
    last_removed_label = None  # 记录最后导致断连的标签

    # 步骤2：随机删标签至s-t断连
    while mss_graph.is_connected(s, t):
        if not all_labels:
            raise ValueError("所有标签已删除，s-t仍连通")
        # a. 均匀随机选择一个标签ℓ
        selected_label = random.choice(list(all_labels))
        # b. 移除该标签的所有边
        mss_graph.remove_label(selected_label)
        # c. 从标签集中删除该标签
        all_labels.remove(selected_label)
        # d. 记录当前删除的标签
        last_removed_label = selected_label

    # 步骤3：恢复最后一个标签（使s-t重新连通）
    if last_removed_label is not None:
        mss_graph.restore_label(original_graph, last_removed_label)
        all_labels.add(last_removed_label)

    # 步骤4：移除冗余标签（保证MSS的极小性）
    necessary_labels = remove_redundant_labels(mss_graph, s, t)

    return necessary_labels