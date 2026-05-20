import json
import os
import random
import time
import zlib
from dataclasses import dataclass
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from matplotlib import font_manager

from src import LabeledGraph, monte_carlo_heuristic, monte_carlo_msg_only_heuristic


RESULT_DIR = os.path.join("results", "performance_results", "msgonly")
INSTANCE_DIR = "test_instances"
os.makedirs(RESULT_DIR, exist_ok=True)

candidate_fonts = [
    "PingFang SC",
    "Hiragino Sans GB",
    "Heiti SC",
    "STHeiti",
    "Songti SC",
    "Arial Unicode MS",
    "Microsoft YaHei",
    "SimHei",
    "Noto Sans CJK SC",
    "WenQuanYi Zen Hei",
]
available_fonts = {f.name for f in font_manager.fontManager.ttflist}
chosen_font = next((name for name in candidate_fonts if name in available_fonts), None)
if chosen_font:
    plt.rcParams["font.sans-serif"] = [chosen_font]
else:
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


@dataclass
class BenchConfig:
    n: int
    p: float
    q: int
    instances: int


def read_test_instance(file_path: str) -> tuple[LabeledGraph, int, int]:
    """读取测试实例TXT文件，格式与主启发式脚本保持一致。"""
    graph = LabeledGraph()
    s = 0
    t = 0
    reading_edges = False

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                if line.startswith("n:"):
                    n = int(line.split(":")[1].strip())
                    graph = LabeledGraph(n)
                elif line.startswith("s:"):
                    s = int(line.split(":")[1].strip())
                elif line.startswith("t:"):
                    t = int(line.split(":")[1].strip())
                elif line == "E:":
                    reading_edges = True
                    continue
                if reading_edges:
                    parts = line.split()
                    if len(parts) == 3:
                        u, v, label = int(parts[0]), int(parts[1]), int(parts[2])
                        graph.add_edge(u, v, label)
            except ValueError as e:
                raise ValueError(f"文件{file_path}第{line_num}行解析错误：{e}")

    if s not in graph.G.nodes() or t not in graph.G.nodes():
        raise ValueError(f"实例{file_path}中s={s}或t={t}超出顶点范围")
    return graph, s, t


def _to_labeled_graph(nx_graph: nx.Graph, q: int, seed: int) -> Tuple[LabeledGraph, int, int]:
    rng = random.Random(seed)
    nodes = sorted(nx_graph.nodes())
    mapping = {node: idx for idx, node in enumerate(nodes)}

    graph = LabeledGraph(len(nodes))
    for u, v in nx_graph.edges():
        graph.add_edge(mapping[u], mapping[v], rng.randint(0, q - 1))

    return graph, 0, len(nodes) - 1


def run_single_instance(graph: LabeledGraph, s: int, t: int, max_score: int, seed: int) -> Dict[str, float]:
    start = time.perf_counter()
    cut_msg, size_msg = monte_carlo_msg_only_heuristic(
        graph, s, t, max_score=max_score, random_seed=seed
    )
    msg_time = time.perf_counter() - start

    start = time.perf_counter()
    cut_dual, size_dual = monte_carlo_heuristic(
        graph, s, t, max_score=max_score, random_seed=seed
    )
    dual_time = time.perf_counter() - start

    g1 = graph.copy()
    for label in cut_msg:
        g1.remove_label(label)
    msg_valid = not g1.is_connected(s, t)

    g2 = graph.copy()
    for label in cut_dual:
        g2.remove_label(label)
    dual_valid = not g2.is_connected(s, t)

    improvement_pct = 0.0
    if size_msg > 0:
        improvement_pct = (size_msg - size_dual) / size_msg * 100.0

    time_ratio = float("inf") if msg_time == 0 else dual_time / msg_time

    return {
        "msg_cut_size": size_msg,
        "dual_cut_size": size_dual,
        "msg_runtime_s": round(msg_time, 6),
        "dual_runtime_s": round(dual_time, 6),
        "msg_valid": int(msg_valid),
        "dual_valid": int(dual_valid),
        "improvement_pct": round(improvement_pct, 4),
        "dual_time_ratio_vs_msg": round(time_ratio, 4),
        "dual_win": int(size_dual < size_msg),
        "tie": int(size_dual == size_msg),
    }


def _instance_id(file_name: str) -> int:
    base_name = os.path.basename(file_name)
    parts = base_name.split("_")
    for part in parts:
        if part.isdigit():
            return int(part)
    return 10**9


def _stable_seed(master_seed: int, dataset: str, n: int, p: float, idx: int) -> int:
    payload = f"{dataset}|{n}|{p:.3f}|{idx}".encode("utf-8")
    return master_seed + (zlib.crc32(payload) % (10**7))


def save_plots(df: pd.DataFrame) -> None:
    summary = df.groupby("顶点数n", as_index=False).agg(
        dual_win_rate=("dual_win", "mean"),
        avg_improvement_pct=("improvement_pct", "mean"),
        avg_time_ratio=("dual_time_ratio_vs_msg", "mean"),
    )

    plt.figure(figsize=(10, 4.8))
    plt.bar(summary["顶点数n"].astype(str), summary["dual_win_rate"] * 100, color="#3C8DAD")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("胜率 (%)")
    plt.title("MSG+MSS 相对 MSG-only 的胜率（按顶点数）")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULT_DIR, "win_rate_by_n.png"), dpi=220)
    plt.close()

    plt.figure(figsize=(10, 4.8))
    plt.bar(summary["顶点数n"].astype(str), summary["avg_improvement_pct"], color="#4C956C")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("平均改进 (%)")
    plt.title("MSG+MSS 的平均改进百分比（按顶点数）")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULT_DIR, "avg_improvement_by_n.png"), dpi=220)
    plt.close()

    plt.figure(figsize=(10, 4.8))
    plt.bar(summary["顶点数n"].astype(str), summary["avg_time_ratio"], color="#B56576")
    plt.axhline(1.0, color="#333333", linestyle="--", linewidth=1)
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("时间开销比 (dual/msg)")
    plt.title("MSG+MSS 的时间开销比（按顶点数）")
    plt.tight_layout()
    plt.savefig(os.path.join(RESULT_DIR, "time_ratio_by_n.png"), dpi=220)
    plt.close()


def main() -> None:
    master_seed = 20260402
    max_score = 120
    rows: List[Dict[str, float]] = []

    if not os.path.exists(INSTANCE_DIR):
        raise FileNotFoundError(f"测试实例目录不存在: {INSTANCE_DIR}")

    instance_files = [
        os.path.join(INSTANCE_DIR, name)
        for name in sorted(os.listdir(INSTANCE_DIR))
        if name.endswith(".txt")
    ]

    if not instance_files:
        raise RuntimeError(f"{INSTANCE_DIR} 中没有可用的 TXT 实例")

    for idx, file_path in enumerate(instance_files):
        graph, s, t = read_test_instance(file_path)
        n = graph.G.number_of_nodes()
        q = len(graph.get_all_labels())
        m = graph.G.number_of_edges()
        seed = _stable_seed(master_seed, os.path.basename(file_path), n, float(m), idx)

        result = run_single_instance(graph, s, t, max_score=max_score, seed=seed)
        rows.append(
            {
                "文件名": os.path.basename(file_path),
                "实例编号": _instance_id(file_path),
                "顶点数n": n,
                "边数m": m,
                "标签数q": q,
                **result,
            }
        )

    df = pd.DataFrame(rows)
    detail_path = os.path.join(RESULT_DIR, "instance_level_results.csv")
    df.to_csv(detail_path, index=False, encoding="utf-8-sig")

    summary = df.groupby("顶点数n", as_index=False).agg(
        instances=("文件名", "size"),
        dual_win_rate=("dual_win", "mean"),
        tie_rate=("tie", "mean"),
        avg_improvement_pct=("improvement_pct", "mean"),
        avg_msg_runtime_s=("msg_runtime_s", "mean"),
        avg_dual_runtime_s=("dual_runtime_s", "mean"),
        avg_time_ratio=("dual_time_ratio_vs_msg", "mean"),
        msg_valid_rate=("msg_valid", "mean"),
        dual_valid_rate=("dual_valid", "mean"),
    )

    summary["dual_win_rate"] = (summary["dual_win_rate"] * 100).round(2)
    summary["tie_rate"] = (summary["tie_rate"] * 100).round(2)
    summary["msg_valid_rate"] = (summary["msg_valid_rate"] * 100).round(2)
    summary["dual_valid_rate"] = (summary["dual_valid_rate"] * 100).round(2)
    summary["avg_improvement_pct"] = summary["avg_improvement_pct"].round(3)
    summary["avg_msg_runtime_s"] = summary["avg_msg_runtime_s"].round(4)
    summary["avg_dual_runtime_s"] = summary["avg_dual_runtime_s"].round(4)
    summary["avg_time_ratio"] = summary["avg_time_ratio"].round(3)

    summary_path = os.path.join(RESULT_DIR, "summary_by_n.csv")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    overall = {
        "instances_total": int(len(df)),
        "dual_win_rate_pct": round(float(df["dual_win"].mean() * 100), 2),
        "tie_rate_pct": round(float(df["tie"].mean() * 100), 2),
        "avg_improvement_pct": round(float(df["improvement_pct"].mean()), 3),
        "avg_time_ratio_dual_vs_msg": round(float(df["dual_time_ratio_vs_msg"].mean()), 3),
        "msg_valid_rate_pct": round(float(df["msg_valid"].mean() * 100), 2),
        "dual_valid_rate_pct": round(float(df["dual_valid"].mean() * 100), 2),
        "notes": {
            "note": "与启发式算法的全规模测试保持同一批 test_instances/*.txt 实例",
        },
    }

    with open(os.path.join(RESULT_DIR, "overall_summary.json"), "w", encoding="utf-8") as f:
        json.dump(overall, f, ensure_ascii=False, indent=2)

    save_plots(df)

    print("=== Unified Benchmark Done ===")
    print(f"详细结果: {detail_path}")
    print(f"数据集汇总: {summary_path}")
    print(f"总体汇总: {os.path.join(RESULT_DIR, 'overall_summary.json')}")


if __name__ == "__main__":
    main()