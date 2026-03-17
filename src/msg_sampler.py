from src.graph_base import LabeledGraph
from src.utils import remove_redundant_labels
from typing import Tuple
import random

def sample_msg(original_graph: LabeledGraph, s: int, t: int, random_seed: int = None) -> Tuple[LabeledGraph, set]:
    """
    Algorithm2：基于Prim的MSG采样（修复边界标签计算BUG）
    :param original_graph: 原始带标签图
    :param s: 源点
    :param t: 汇点
    :param random_seed: 随机种子（None则使用全局种子）
    :return: (MSG子图, 必要标签集)
    """
    if random_seed is not None:
        random.seed(random_seed)
    
    # 边界检查
    if s not in original_graph.G.nodes() or t not in original_graph.G.nodes():
        raise ValueError(f"源点s={s}或汇点t={t}不在图中")
    
    # 步骤1：初始化空图（仅顶点）
    msg_graph = LabeledGraph()
    msg_graph.G.add_nodes_from(original_graph.G.nodes())

    # 步骤2：循环扩展直到s-t连通
    max_expand_steps = max(1, len(original_graph.get_all_labels()) * 2)
    expand_steps = 0
    while not msg_graph.is_connected(s, t):
        expand_steps += 1
        if expand_steps > max_expand_steps:
            raise RuntimeError(
                f"MSG扩展超过上限({max_expand_steps})仍未连通，可能存在无进展循环"
            )

        # 1. 获取边界标签
        boundary_labels = msg_graph.get_boundary_labels(s, original_graph.edge_to_label)
        
        # 修复BUG：过滤掉已在MSG中的标签，避免重复添加
        boundary_labels = set(boundary_labels) - msg_graph.get_all_labels()
        
        # 2. 如果过滤后没有可用边界标签，触发兜底逻辑
        if not boundary_labels:
            boundary_labels = original_graph.get_all_labels() - msg_graph.get_all_labels()
            
        # 3. 兜底后如果依然为空（极端断连情况），抛出异常避免死循环
        if not boundary_labels:
            raise RuntimeError(f"无法连通 s={s} 和 t={t}，且无剩余标签可供扩展")
            
        # 4. 随机选择一个标签并添加到图中
        chosen_label = random.choice(list(boundary_labels))
        msg_graph.restore_label(original_graph, chosen_label)


    # 步骤3：移除冗余标签
    necessary_labels = remove_redundant_labels(msg_graph, s, t)

    # 移除孤立点
    isolated = [n for n in msg_graph.G.nodes if msg_graph.G.degree(n) == 0]
    msg_graph.G.remove_nodes_from(isolated)

    return msg_graph, necessary_labels