import random
import json
from pathlib import Path
from src.graph import LabeledGraph

def generate_test_instance(
    n_vertices: int,  # 顶点数
    edge_prob: float,  # 边生成概率（0-1）
    n_labels: int,     # 标签总数
    s: int = 0,        # 源点
    t: int = 1         # 汇点
) -> LabeledGraph:
    """生成随机测试实例（Gnp模型）"""
    graph = LabeledGraph()
    # 添加顶点（编号0到n_vertices-1）
    for v in range(n_vertices):
        graph.add_vertex(v)
    # 随机生成边和标签
    labels = [str(lbl) for lbl in range(n_labels)]
    for u in range(n_vertices):
        for v in range(u+1, n_vertices):
            if random.random() < edge_prob:
                # 随机分配标签
                lbl = random.choice(labels)
                graph.add_edge(u, v, lbl)
    # 确保s和t连通（如果不连通，添加一条边）
    while not graph.is_connected(s, t):
        lbl = random.choice(labels)
        graph.add_edge(s, random.choice(range(n_vertices)), lbl)
    return graph

def save_graph_to_json(graph: LabeledGraph, save_path: str):
    """将图保存为JSON（方便复用）"""
    data = {
        "edges": [],
        "s": 0,
        "t": 1
    }
    for edge, lbl in graph.edge_labels.items():
        u, v = tuple(edge)
        data["edges"].append({"u": u, "v": v, "label": lbl})
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_graph_from_json(load_path: str) -> Tuple[LabeledGraph, int, int]:
    """从JSON加载图"""
    with open(load_path, 'r') as f:
        data = json.load(f)
    graph = LabeledGraph()
    for edge in data["edges"]:
        u = edge["u"]
        v = edge["v"]
        lbl = edge["label"]
        graph.add_vertex(u)
        graph.add_vertex(v)
        graph.add_edge(u, v, lbl)
    return graph, data["s"], data["t"]

def generate_all_test_instances():
    """生成10+个测试实例（满足任务书要求）"""
    # 小规模实例（用于枚举最优解）
    small_params = [
        (5, 0.6, 3),   # 5顶点，边概率0.6，3标签
        (6, 0.5, 4),   # 6顶点，边概率0.5，4标签
        (8, 0.4, 5)    # 8顶点，边概率0.4，5标签
    ]
    for i, (n, p, lbl) in enumerate(small_params):
        graph = generate_test_instance(n, p, lbl)
        save_graph_to_json(graph, f"data/small/instance_{i+1}.json")

    # 中等规模实例
    medium_params = [
        (10, 0.5, 8), (15, 0.4, 10), (20, 0.3, 15), (25, 0.3, 20), (30, 0.2, 25)
    ]
    for i, (n, p, lbl) in enumerate(medium_params):
        graph = generate_test_instance(n, p, lbl)
        save_graph_to_json(graph, f"data/medium/instance_{i+1}.json")

    # 大规模实例
    large_params = [
        (40, 0.2, 30), (50, 0.15, 40), (60, 0.1, 50), (80, 0.1, 60)
    ]
    for i, (n, p, lbl) in enumerate(large_params):
        graph = generate_test_instance(n, p, lbl)
        save_graph_to_json(graph, f"data/large/instance_{i+1}.json")

if __name__ == "__main__":
    # 运行此脚本生成所有测试数据
    generate_all_test_instances()
    print("所有测试实例生成完成！")