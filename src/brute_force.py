"""
小规模标签s-t割问题 暴力枚举最优解
适配自动生成的小规模测试用例（n≤15），结果单独保存到results文件夹
"""
import itertools
import json
import os
import re
import sys
import traceback
import math
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.append(str(PROJECT_ROOT))
from src.graph_base import LabeledGraph  
from src.config import SMALL_SCALE_THRESHOLD

# ===================== 配置项 =====================
INSTANCE_DIR = PROJECT_ROOT / "test_instances"  # 测试实例文件夹
RESULT_DIR = PROJECT_ROOT / "results" / "algorithm_results"  # 枚举+启发式结果目录
RESULT_FILE = RESULT_DIR / "brute_force_optimal_results.json"  # 结果文件路径

def read_test_instance(file_path: str) -> tuple[LabeledGraph, int, int]:
    """读取测试实例TXT文件"""
    try:
        graph = LabeledGraph()
        s = 0
        t = 0
        reading_edges = False

        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
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
                    if reading_edges:
                        parts = line.split()
                        if len(parts) == 3:
                            u, v, label = int(parts[0]), int(parts[1]), int(parts[2])
                            graph.add_edge(u, v, label)
                except ValueError as e:
                    raise ValueError(f"文件{file_path}第{line_num}行解析错误：{e}")
        
        # 验证s/t合法性
        if s not in graph.G.nodes() or t not in graph.G.nodes():
            raise ValueError(f"s={s}或t={t}不在图的顶点集中")
        return graph, s, t
    except Exception as e:
        raise RuntimeError(f"读取实例{file_path}失败：{e}")

def brute_force_optimal_cut(graph: LabeledGraph, s: int, t: int) -> tuple[int, list[int]]:
    """枚举最优标签割集（优化效率：找到最小割集立即返回）
    返回：(最优割集大小, 最优割集标签列表)
    """
    labels = list(graph.get_all_labels())
    q = len(labels)
    min_size = float('inf')
    best_cut = []

    if q == 0:
        return 0, []
    
    print(f"【枚举】总标签数：{q}，最小割集枚举中...")
    
    # 从小到大枚举子集大小（找到最小的割集就立即返回，无需枚举更大子集）
    for size in range(1, q+1):
        subset_count = math.comb(q, size)
        print(f"【枚举】检查大小为{size}的子集（共{subset_count}个）...")
        
        # 分批枚举，避免内存溢出
        batch_size = 1000
        for idx, cut in enumerate(itertools.combinations(labels, size)):
            # 进度提示（每batch_size次打印一次）
            if idx % batch_size == 0 and idx > 0:
                progress = (idx / subset_count) * 100
                print(f"  进度：{idx}/{subset_count} ({progress:.1f}%)")
            
            # 复制图并移除当前割集的标签
            temp_g = graph.copy()
            for label in cut:
                temp_g.remove_label(label)
            
            # 检查是否断连
            if not temp_g.is_connected(s, t):
                min_size = size
                best_cut = list(cut)
                print(f"【枚举】找到最优解！大小={min_size}, 割集={best_cut}")
                return min_size, best_cut
    
    # 极端情况：所有标签都要移除
    print(f"【枚举】需移除所有标签才能断开s={s}-t={t}，割集大小={q}")
    return q, labels

def save_brute_force_results(all_results: list):
    """保存所有小规模实例的枚举结果（追加模式，避免覆盖）"""
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 读取历史结果
    existing_results = []
    if RESULT_FILE.exists():
        try:
            with open(RESULT_FILE, "r", encoding="utf-8") as f:
                existing_results = json.load(f)
        except json.JSONDecodeError:
            print(f"【警告】历史结果文件{RESULT_FILE}格式错误，将覆盖")
    
    # 去重：按instance_name覆盖
    result_dict = {item["instance_name"]: item for item in existing_results}
    for new_item in all_results:
        result_dict[new_item["instance_name"]] = new_item
    merged_results = list(result_dict.values())
    
    # 写入JSON
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(merged_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n【保存】枚举最优解结果已写入：{RESULT_FILE}（共{len(merged_results)}个实例）")
    return str(RESULT_FILE)

def print_summary(all_results: list):
    """打印批量处理的汇总统计信息"""
    if not all_results:
        return
    
    print("\n" + "="*80)
    print("【批量处理汇总】")
    print("="*80)
    n_groups = {}
    total_instances = len(all_results)
    total_opt_size = 0
    
    for res in all_results:
        n = res["parameters"]["n"]
        opt_size = res["optimal_cut_size"]
        total_opt_size += opt_size
        
        if n not in n_groups:
            n_groups[n] = {"count": 0, "total_opt_size": 0}
        n_groups[n]["count"] += 1
        n_groups[n]["total_opt_size"] += opt_size
    
    print(f"处理实例总数：{total_instances}")
    print(f"平均最优割集大小：{total_opt_size/total_instances:.2f}")
    print("\n按顶点数n分组统计：")
    for n in sorted(n_groups.keys()):
        count = n_groups[n]["count"]
        avg_opt = n_groups[n]["total_opt_size"] / count
        print(f"  n={n}：{count}个实例，平均最优割集大小={avg_opt:.2f}")

def run_brute_force(instance_path: str = None):
    """运行暴力枚举（支持单个实例/批量实例）"""
    all_results = []
    
    if instance_path:
        instance_files = [instance_path]
    else:
        # 批量处理小规模实例
        if not INSTANCE_DIR.exists():
            print(f"【错误】实例目录不存在：{INSTANCE_DIR}")
            return
        
        instance_files = []
        for file in os.listdir(INSTANCE_DIR):
            if not file.endswith(".txt"):
                continue
            match = re.search(r"_n(\d+)_", file)
            if not match:
                continue
            n_value = int(match.group(1))
            if n_value <= SMALL_SCALE_THRESHOLD:
                instance_files.append(str(INSTANCE_DIR / file))
        
        if not instance_files:
            print(f"未找到小规模测试实例！目录：{INSTANCE_DIR}，请先生成实例")
            return
    
    # 遍历实例运行枚举法
    for file_path in instance_files:
        filename = os.path.basename(file_path)
        print("\n" + "="*60)
        print(f"【处理实例】{filename}")
        print("="*60)
        
        try:
            graph, s, t = read_test_instance(file_path)
            n = graph.G.number_of_nodes()
            q = len(graph.get_all_labels())
            
            if n > SMALL_SCALE_THRESHOLD:
                print(f"跳过大规模实例：{filename} (n={n} > {SMALL_SCALE_THRESHOLD})")
                continue
            
            # 运行枚举法
            optimal_size, optimal_cut = brute_force_optimal_cut(graph, s, t)
            
            # 记录结果
            result = {
                "instance_name": filename,
                "parameters": {
                    "n": n,
                    "q": q,
                    "s": s,
                    "t": t
                },
                "optimal_cut_size": optimal_size,
                "optimal_cut_labels": optimal_cut
            }
            all_results.append(result)
            
            # 打印单实例结果
            print(f"\n【实例 {filename} 结果】")
            print(f"顶点数n={n}, 标签数q={q}")
            print(f"最优割集大小：{optimal_size}")
            print(f"最优割集标签：{optimal_cut}")
        
        except Exception as e:
            print(f"【错误】处理实例{filename}失败：{e}")
            traceback.print_exc()
            continue
    
    # 保存结果+打印汇总
    if all_results:
        save_brute_force_results(all_results)
        print_summary(all_results)
    else:
        print("未成功处理任何实例！")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 处理单个实例
        test_file = sys.argv[1]
        if os.path.exists(test_file):
            run_brute_force(test_file)
        else:
            print(f"【错误】指定的实例文件不存在：{test_file}")
    else:
        # 批量处理所有小规模实例
        run_brute_force()