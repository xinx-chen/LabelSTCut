import csv
import json
import os
import re
import time
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt
from matplotlib import font_manager

from src.brute_force import brute_force_optimal_cut, read_test_instance
from src.config import SMALL_SCALE_THRESHOLD

PROJECT_ROOT = Path(__file__).parent
INSTANCE_DIR = PROJECT_ROOT / "test_instances"
RESULT_DIR = PROJECT_ROOT / "results" / "bruteforce_results"


def _setup_chinese_font() -> None:
    candidates = [
        "PingFang SC",
        "Hiragino Sans GB",
        "Heiti SC",
        "STHeiti",
        "Songti SC",
        "Arial Unicode MS",
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((name for name in candidates if name in available), None)
    if chosen:
        plt.rcParams["font.sans-serif"] = [chosen]
    else:
        plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


def _instance_id(file_name: str) -> int:
    match = re.search(r"instance_(\d+)", file_name)
    return int(match.group(1)) if match else 10**9


def collect_bruteforce_results() -> list[dict]:
    if not INSTANCE_DIR.exists():
        raise FileNotFoundError(f"实例目录不存在: {INSTANCE_DIR}")

    txt_files = sorted(
        [p for p in INSTANCE_DIR.iterdir() if p.suffix == ".txt"],
        key=lambda p: _instance_id(p.name),
    )

    rows: list[dict] = []
    for path in txt_files:
        graph, s, t = read_test_instance(str(path))
        n = graph.G.number_of_nodes()
        if n > SMALL_SCALE_THRESHOLD:
            continue

        q = len(graph.get_all_labels())
        t0 = time.time()
        optimal_size, optimal_cut = brute_force_optimal_cut(graph, s, t)
        run_time = round(time.time() - t0, 6)

        rows.append(
            {
                "instance_name": path.name,
                "instance_id": _instance_id(path.name),
                "n": n,
                "q": q,
                "s": s,
                "t": t,
                "optimal_cut_size": int(optimal_size),
                "optimal_cut_labels": list(optimal_cut),
                "run_time_s": run_time,
            }
        )

    return rows


def save_results(rows: list[dict]) -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    json_path = RESULT_DIR / "brute_force_results_detailed.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    csv_path = RESULT_DIR / "brute_force_results_detailed.csv"
    fieldnames = [
        "instance_name",
        "instance_id",
        "n",
        "q",
        "s",
        "t",
        "optimal_cut_size",
        "optimal_cut_labels",
        "run_time_s",
    ]
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row_copy = row.copy()
            row_copy["optimal_cut_labels"] = " ".join(map(str, row_copy["optimal_cut_labels"]))
            writer.writerow(row_copy)

    if not rows:
        summary = {
            "instance_count": 0,
            "small_scale_threshold": SMALL_SCALE_THRESHOLD,
        }
    else:
        by_n: dict[int, list[dict]] = {}
        for r in rows:
            by_n.setdefault(r["n"], []).append(r)
        summary = {
            "instance_count": len(rows),
            "small_scale_threshold": SMALL_SCALE_THRESHOLD,
            "avg_optimal_cut_size": round(mean(r["optimal_cut_size"] for r in rows), 4),
            "avg_runtime_s": round(mean(r["run_time_s"] for r in rows), 6),
            "max_runtime_s": max(r["run_time_s"] for r in rows),
            "min_runtime_s": min(r["run_time_s"] for r in rows),
            "by_n": {
                str(n): {
                    "count": len(group),
                    "avg_optimal_cut_size": round(mean(g["optimal_cut_size"] for g in group), 4),
                    "avg_runtime_s": round(mean(g["run_time_s"] for g in group), 6),
                }
                for n, group in sorted(by_n.items())
            },
        }

    with open(RESULT_DIR / "brute_force_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


def plot_results(rows: list[dict]) -> None:
    if not rows:
        return

    _setup_chinese_font()
    rows = sorted(rows, key=lambda r: r["instance_id"])

    labels = [f"i{r['instance_id']}" for r in rows]
    x = list(range(len(rows)))

    # 图1：最优割集大小
    plt.figure(figsize=(14, 5.8))
    plt.bar(x, [r["optimal_cut_size"] for r in rows], color="#4C78A8")
    plt.xticks(x, labels, rotation=70, ha="right", fontsize=8)
    plt.ylabel("最优割集大小")
    plt.xlabel("实例")
    plt.title("暴力枚举：各实例最优割集大小")
    plt.tight_layout()
    plt.savefig(RESULT_DIR / "optimal_cut_size_by_instance.png", dpi=220)
    plt.close()

    # 图2：运行时间
    plt.figure(figsize=(14, 5.8))
    plt.plot(x, [r["run_time_s"] for r in rows], marker="o", linewidth=1.5, color="#F58518")
    plt.xticks(x, labels, rotation=70, ha="right", fontsize=8)
    plt.ylabel("运行时间 (s)")
    plt.xlabel("实例")
    plt.title("暴力枚举：各实例运行时间")
    plt.tight_layout()
    plt.savefig(RESULT_DIR / "runtime_by_instance.png", dpi=220)
    plt.close()

    # 图3：q 与最优割集大小关系
    plt.figure(figsize=(8, 6))
    plt.scatter(
        [r["q"] for r in rows],
        [r["optimal_cut_size"] for r in rows],
        c=[r["n"] for r in rows],
        cmap="viridis",
        s=50,
        alpha=0.85,
    )
    plt.colorbar(label="顶点数 n")
    plt.xlabel("标签数 q")
    plt.ylabel("最优割集大小")
    plt.title("暴力枚举：q 与最优割集大小关系")
    plt.tight_layout()
    plt.savefig(RESULT_DIR / "optimal_cut_vs_q_scatter.png", dpi=220)
    plt.close()


def main() -> None:
    rows = collect_bruteforce_results()
    save_results(rows)
    plot_results(rows)
    print(f"已生成枚举结果目录: {RESULT_DIR}")
    print(f"实例数: {len(rows)}")


if __name__ == "__main__":
    main()
