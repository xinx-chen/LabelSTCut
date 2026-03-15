import pandas as pd
from pathlib import Path
from src.utils import load_graph_from_json
from src.heuristic import monte_carlo_heuristic
from src.zft18 import zft18_approx_algorithm
from src.brute_force import brute_force_min_label_cut

def run_all_tests():
    """批量运行所有测试实例，统计结果"""
    results = []
    # 遍历所有测试数据
    data_dirs = ["data/small", "data/medium", "data/large"]
    for data_dir in data_dirs:
        for json_file in Path(data_dir).glob("*.json"):
            print(f"正在测试：{json_file}")
            # 加载图
            graph, s, t = load_graph_from_json(str(json_file))
            n_vertices = graph.get_vertex_count()
            n_edges = graph.get_edge_count()
            n_labels = len(graph.get_all_labels())

            # 运行算法
            # 1. 蒙特卡洛启发式算法
            heuristic_cut = monte_carlo_heuristic(graph, s, t)
            heuristic_size = len(heuristic_cut)

            # 2. ZFT18近似算法
            zft18_cut = zft18_approx_algorithm(graph, s, t)
            zft18_size = len(zft18_cut)

            # 3. 小规模实例运行枚举法（最优解）
            opt_size = None
            if data_dir == "data/small":
                opt_cut = brute_force_min_label_cut(graph, s, t)
                opt_size = len(opt_cut)

            # 保存结果
            results.append({
                "实例路径": str(json_file),
                "顶点数": n_vertices,
                "边数": n_edges,
                "标签数": n_labels,
                "启发式算法大小": heuristic_size,
                "ZFT18算法大小": zft18_size,
                "最优解大小": opt_size,
                "启发式vs最优解（比率）": heuristic_size / opt_size if opt_size else None,
                "启发式vsZFT18（比率）": heuristic_size / zft18_size
            })

    # 保存结果到CSV
    df = pd.DataFrame(results)
    Path("results").mkdir(exist_ok=True)
    df.to_csv("results/result.csv", index=False, encoding="utf-8-sig")
    print("所有测试完成！结果已保存到 results/result.csv")
    return df

if __name__ == "__main__":
    # 运行所有测试
    run_all_tests()