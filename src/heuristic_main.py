from src.graph_base import LabeledGraph
from src.msg_sampler import sample_msg
from src.mss_sampler import sample_mss
from typing import Dict, List, Tuple
import random

# 【修复】DEBUG模式日志BUG（提前定义all_labels）
DEBUG_MODE = False

def monte_carlo_heuristic(original_graph: LabeledGraph, s: int, t: int, max_score: int = 120, random_seed: int = 42) -> Tuple[List[int], int]:
    """
    Algorithm1：蒙特卡洛启发式主算法
    :param original_graph: 原始带标签图
    :param s: 源点
    :param t: 汇点
    :param max_score: 采样迭代次数（论文默认100）
    :param random_seed: 随机种子（保证可复现）
    :return: (最终标签割集C, 割集大小|C|)
    """
    # 步骤1：初始化标签得分和工作图
    all_labels = original_graph.get_all_labels()
    
    # DEBUG日志修复：仅在有标签时打印
    if DEBUG_MODE and all_labels:
        print(f"【DEBUG】主算法开始，总标签数：{len(all_labels)}")
    
    # 初始化标签得分
    label_score: Dict[int, int] = {label: 0 for label in all_labels}
    work_graph = original_graph.copy()  # 工作图（用于选标签，不修改原图）

    # 步骤2：标签打分阶段（循环max_score次）
    random.seed(random_seed)  # 统一随机种子
    for _ in range(max_score):
        try:
            # a. 采样MSG并打分
            _, msg_labels = sample_msg(original_graph, s, t)
            for label in msg_labels:
                if label in label_score:
                    label_score[label] += 1
            
            # b. 采样MSS并打分
            mss_labels = sample_mss(original_graph, s, t)
            for label in mss_labels:
                if label in label_score:
                    label_score[label] += 1
        except ValueError as e:
            if DEBUG_MODE:
                print(f"【DEBUG】采样过程警告：{e}")
            continue

    # 步骤3：解构造阶段（按得分降序选标签）
    if not label_score:
        return [], 0  # 无标签时直接返回空割集
    
    # 按得分降序排序标签（得分相同则随机排序）
    sorted_labels = sorted(
        label_score.items(), 
        key=lambda x: (-x[1], random.random())
    )
    final_cut = []

    for label, _ in sorted_labels:
        # 移除当前标签的所有边
        work_graph.remove_label(label)
        final_cut.append(label)
        # 判断s-t是否断连
        if not work_graph.is_connected(s, t):
            break

    # 步骤4：返回最终割集和大小
    return final_cut, len(final_cut)