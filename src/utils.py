from src.graph_base import LabeledGraph 
from typing import Set, List
import random
import os
import json

def remove_redundant_labels(graph: LabeledGraph, s: int, t: int, random_seed: int = 42) -> Set[int]:
    """
    冗余标签移除：对图中的标签逐个测试，移除不影响s-t连通性的标签
    :param graph: 待处理的图（MSG或MSS对应的图）
    :param s: 源点
    :param t: 汇点
    :param random_seed: 随机种子（保证标签顺序可复现）
    :return: 移除冗余后的标签集合
    """
    # 1. 获取当前图的所有标签，随机排序
    labels = list(graph.get_all_labels())
    random.seed(random_seed)
    random.shuffle(labels)

    # 2. 逐个测试标签是否冗余
    necessary_labels = set()
    for label in labels:
        # 临时移除该标签
        temp_graph = graph.copy()
        temp_graph.remove_label(label)
        # 判断移除后s-t是否仍连通
        if temp_graph.is_connected(s, t):
            # 连通→冗余，永久移除
            graph.remove_label(label)
        else:
            # 不连通→必要，保留
            necessary_labels.add(label)

    return necessary_labels

def get_test_instances(dir_path, small_only=True):
    """获取测试实例路径列表"""
    instances = []
    for root, _, files in os.walk(dir_path):
        for f in files:
            if f.endswith(".json"):
                instances.append(os.path.join(root, f))
    return instances

def load_graph(file_path):
    """从json文件加载LabeledGraph"""
    with open(file_path, "r") as f:
        data = json.load(f)
    graph = LabeledGraph()
    for edge in data["edges"]:
        graph.add_edge(edge["u"], edge["v"], label=edge["label"])
    return graph