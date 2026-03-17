from src import LabeledGraph, monte_carlo_heuristic
from src.brute_force import brute_force_optimal_cut
import os
import time

# ===================== 路径配置 =====================
RESULT_ROOT_DIR = "results"  # 结果根目录
ALGO_RESULT_DIR = os.path.join(RESULT_ROOT_DIR, "algorithm_results")  # 枚举+启发式结果
INSTANCE_DIR = "test_instances"  # 测试实例文件夹

# ===================== DEBUG配置 =====================
DEBUG_MODE = True  # 调试模式开关（True=打印详细过程，False=简洁输出）
BATCH_TEST = True   # 批量测试所有实例
MAX_SCORE = 120    # 论文固定参数
RANDOM_SEED = 42 # 固定随机种子，实验可复现

def read_test_instance(file_path: str) -> tuple[LabeledGraph, int, int]:
    """读取测试实例TXT文件（增强异常处理）"""
    graph = LabeledGraph()
    s = 0
    t = 0
    reading_edges = False

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # 解析参数
            try:
                if line.startswith('n:'):
                    n = int(line.split(':')[1].strip())
                    graph = LabeledGraph(n)
                elif line.startswith('s:'):
                    s = int(line.split(':')[1].strip())
                elif line.startswith('t:'):
                    t = int(line.split(':')[1].strip())
                elif line == 'E:':
                    reading_edges = True
                    continue
                # 解析边
                if reading_edges:
                    parts = line.split()
                    if len(parts) == 3:
                        u, v, label = int(parts[0]), int(parts[1]), int(parts[2])
                        graph.add_edge(u, v, label)
            except ValueError as e:
                raise ValueError(f"文件{file_path}第{line_num}行解析错误：{e}")
    
    # 验证s/t合法性
    if s not in graph.G.nodes() or t not in graph.G.nodes():
        raise ValueError(f"实例{file_path}中s={s}或t={t}超出顶点范围")
    return graph, s, t

def test_single_instance(file_path: str):
    """测试单个实例"""
    filename = os.path.basename(file_path)
    print("\n" + "="*60)
    print(f"【测试实例】{filename}")
    print("="*60)

    try:
        # 1. 读取实例
        start_time = time.time()
        graph, s, t = read_test_instance(file_path)
        n = graph.G.number_of_nodes()
        m = graph.G.number_of_edges()
        q = len(graph.get_all_labels())

        # 2. 打印基础信息
        print(f"基础信息：顶点={n}, 边={m}, 标签数={q}, s={s}, t={t}")

        # 3. 【手写】小规模实例：枚举最优解
        optimal_size, optimal_cut = -1, []
        if n <= 15:  # 小规模实例阈值
            print(f"\n【运行】暴力枚举最优解（n={n} ≤ 15）...")
            optimal_size, optimal_cut = brute_force_optimal_cut(graph, s, t)

        # 4. 运行蒙特卡洛启发式算法
        print(f"\n【运行】蒙特卡洛启发式算法（max_score={MAX_SCORE}）...")
        final_cut, cut_size = monte_carlo_heuristic(
            graph, s, t, 
            max_score=MAX_SCORE,
            random_seed=RANDOM_SEED
        )
        run_time = round(time.time() - start_time, 3)

        # 5. 验证结果
        verify_g = graph.copy()
        for label in final_cut:
            verify_g.remove_label(label)
        is_correct = not verify_g.is_connected(s, t)

        # 6. 输出结果
        print(f"\n【运行结果】")
        print(f"运行时间：{run_time}s")
        print(f"启发式割集大小：{cut_size}")
        print(f"启发式割集：{final_cut}")
        if optimal_size != -1:
            print(f"最优割集大小：{optimal_size}")
            print(f"最优割集：{optimal_cut}")
            print(f"算法精度：{optimal_size/cut_size*100:.1f}%")
        print(f"结果有效性（s-t断连）：{'有效' if is_correct else '无效'}")
        print(f"{'='*60}\n")

        # 保存结果到日志（写入算法结果分类目录）
        log_path = os.path.join(ALGO_RESULT_DIR, "test_log.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{filename},{n},{q},{cut_size},{optimal_size},{run_time},{is_correct}\n")
    
    except Exception as e:
        print(f"\n【错误】处理实例{filename}失败：{str(e)}")
        # 记录错误日志
        log_path = os.path.join(ALGO_RESULT_DIR, "test_log.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{filename},-1,-1,-1,-1,-1,error:{str(e)}\n")

if __name__ == "__main__":
    # 自动创建结果分类文件夹
    os.makedirs(ALGO_RESULT_DIR, exist_ok=True)
    
    # 初始化日志文件（仅写入一次表头）
    log_path = os.path.join(ALGO_RESULT_DIR, "test_log.txt")
    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("文件名,顶点数,标签数,启发式解,最优解,运行时间,是否有效\n")

    # 读取所有测试实例
    if not os.path.exists(INSTANCE_DIR):
        print(f"【错误】测试实例文件夹不存在：{INSTANCE_DIR}，请先生成实例")
        exit(1)
    
    instance_list = sorted([f for f in os.listdir(INSTANCE_DIR) if f.endswith(".txt")])
    if not instance_list:
        print(f"【错误】{INSTANCE_DIR}文件夹中无TXT测试实例")
        exit(1)

    if BATCH_TEST:
        # 批量测试所有实例
        for file in instance_list:
            test_single_instance(os.path.join(INSTANCE_DIR, file))
    else:
        # 单独测试第一个小规模实例
        test_single_instance(os.path.join(INSTANCE_DIR, instance_list[0]))

    print(f"\n【调试完成】所有测试结果已保存到 -> {ALGO_RESULT_DIR}/test_log.txt")