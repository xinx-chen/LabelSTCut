import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import MaxNLocator

RESULT_ROOT_DIR = "results"
ALGO_RESULT_DIR = os.path.join(RESULT_ROOT_DIR, "algorithm_results")
BRUTEFORCE_RESULT_DIR = os.path.join(RESULT_ROOT_DIR, "bruteforce_results")
PERF_RESULT_DIR = os.path.join(RESULT_ROOT_DIR, "performance_results")
SMALL_COMPARE_DIR = os.path.join(PERF_RESULT_DIR, "small_scale_comparison")
ALL_CASES_DIR = os.path.join(PERF_RESULT_DIR, "all_cases_heuristic")
LEGACY_RESULT_DIR = RESULT_ROOT_DIR
INSTANCE_DIR = "test_instances"

os.makedirs(PERF_RESULT_DIR, exist_ok=True)
os.makedirs(SMALL_COMPARE_DIR, exist_ok=True)
os.makedirs(ALL_CASES_DIR, exist_ok=True)


def resolve_input_path(file_name: str) -> str:
    """优先读取分类目录；若历史文件还在旧目录，自动兼容。"""
    candidate_paths = [
        os.path.join(ALGO_RESULT_DIR, file_name),
        os.path.join(LEGACY_RESULT_DIR, file_name),
    ]
    for path in candidate_paths:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"未找到输入文件: {file_name}。请先运行 main.py / src/brute_force.py 生成算法结果。"
    )


def get_edge_count_from_instance(file_name: str):
    """从同名JSON实例中读取边数m；读取失败时返回None。"""
    json_name = file_name.replace(".txt", ".json")
    json_path = os.path.join(INSTANCE_DIR, json_name)
    if not os.path.exists(json_path):
        return None

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        params = data.get("parameters", {}) if isinstance(data, dict) else {}
        m_value = params.get("m")

        if m_value is not None:
            return int(m_value)

        edges = data.get("edges") if isinstance(data, dict) else None
        if isinstance(edges, list):
            return len(edges)
    except (ValueError, TypeError, json.JSONDecodeError, OSError):
        return None

    return None

# ---------------------- 字体配置（解决中文乱码）----------------------
candidate_fonts = [
    "PingFang SC",         # macOS
    "Hiragino Sans GB",    # macOS
    "Heiti SC",            # macOS old
    "STHeiti",             # macOS old
    "Songti SC",           # macOS
    "Arial Unicode MS",    # macOS optional
    "Microsoft YaHei",     # Windows
    "SimHei",              # Common CJK font
    "Noto Sans CJK SC",    # Linux common
    "WenQuanYi Zen Hei",   # Linux common
]

available_fonts = {
    f.name for f in font_manager.fontManager.ttflist
}
chosen_font = next((name for name in candidate_fonts if name in available_fonts), None)

if chosen_font:
    plt.rcParams["font.sans-serif"] = [chosen_font]
else:
    # 回退到默认字体，至少保证脚本不报错
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]

plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.facecolor"] = "#ffffff"
plt.rcParams["axes.facecolor"] = "#fbfbfc"
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.25
plt.rcParams["grid.linestyle"] = "--"

# ---------------------- 1. 读取你的结果文件 ----------------------
# 从独立枚举目录读取暴力最优解（复用 brute_force_visualize.py 产物）
bruteforce_csv_path = os.path.join(BRUTEFORCE_RESULT_DIR, "brute_force_results_detailed.csv")
if not os.path.exists(bruteforce_csv_path):
    raise FileNotFoundError(
        f"未找到输入文件: {bruteforce_csv_path}。请先运行 brute_force_visualize.py 生成枚举结果。"
    )

optimal_df = pd.read_csv(bruteforce_csv_path, encoding="utf-8-sig")
optimal_df["optimal_cut_size"] = pd.to_numeric(optimal_df["optimal_cut_size"], errors="coerce")
if "run_time_s" in optimal_df.columns:
    optimal_df["run_time_s"] = pd.to_numeric(optimal_df["run_time_s"], errors="coerce")
optimal_df = optimal_df.dropna(subset=["instance_name", "optimal_cut_size"])
optimal_df = optimal_df.drop_duplicates(subset=["instance_name"], keep="last")

# 将最优结果转换成字典，便于按实例名查询
optimal_map = {
    row["instance_name"]: int(row["optimal_cut_size"])
    for _, row in optimal_df.iterrows()
}
bruteforce_time_map = {}
if "run_time_s" in optimal_df.columns:
    bruteforce_time_map = {
        row["instance_name"]: float(row["run_time_s"])
        for _, row in optimal_df.iterrows()
        if pd.notna(row["run_time_s"]) and float(row["run_time_s"]) >= 0
    }

# 读取启发式算法日志（CSV格式）
heuristic_log_path = resolve_input_path("test_log.txt")
heuristic_df = pd.read_csv(heuristic_log_path, encoding="utf-8")

# 日志为追加模式，按实例名去重，仅保留最新一条记录
if "文件名" in heuristic_df.columns:
    heuristic_df = heuristic_df.drop_duplicates(subset=["文件名"], keep="last")

# ---------------------- 1.1 全测试用例数据（蒙特卡洛启发式） ----------------------
heuristic_all_df = heuristic_df.copy()
heuristic_all_df["是否有效_bool"] = (
    heuristic_all_df["是否有效"].astype(str).str.strip().str.lower() == "true"
)
heuristic_all_df["顶点数_num"] = pd.to_numeric(heuristic_all_df["顶点数"], errors="coerce")
heuristic_all_df["标签数_num"] = pd.to_numeric(heuristic_all_df["标签数"], errors="coerce")
heuristic_all_df["启发式解_num"] = pd.to_numeric(heuristic_all_df["启发式解"], errors="coerce")
heuristic_all_df["运行时间_num"] = pd.to_numeric(heuristic_all_df["运行时间"], errors="coerce")
heuristic_all_df["实例编号"] = pd.to_numeric(
    heuristic_all_df["文件名"].astype(str).str.extract(r"instance_(\d+)")[0],
    errors="coerce",
)
heuristic_all_df["边数m_num"] = heuristic_all_df["文件名"].astype(str).map(get_edge_count_from_instance)
heuristic_all_df["边数m_num"] = pd.to_numeric(heuristic_all_df["边数m_num"], errors="coerce")

heuristic_all_df = heuristic_all_df.sort_values(by=["实例编号", "文件名"], na_position="last")

heuristic_valid_df = heuristic_all_df[
    (heuristic_all_df["是否有效_bool"]) &
    (heuristic_all_df["顶点数_num"].notna()) &
    (heuristic_all_df["边数m_num"].notna()) &
    (heuristic_all_df["启发式解_num"].notna()) &
    (heuristic_all_df["运行时间_num"].notna()) &
    (heuristic_all_df["启发式解_num"] >= 0) &
    (heuristic_all_df["运行时间_num"] >= 0)
].copy()

all_cases_table_path = os.path.join(ALL_CASES_DIR, "heuristic_all_cases.csv")
heuristic_valid_df[[
    "文件名", "实例编号", "顶点数_num", "边数m_num", "标签数_num", "启发式解_num", "运行时间_num", "是否有效_bool"
]].rename(columns={
    "顶点数_num": "顶点数n",
    "边数m_num": "边数m",
    "标签数_num": "标签数q",
    "启发式解_num": "启发式割集大小",
    "运行时间_num": "运行时间(s)",
    "是否有效_bool": "是否有效",
}).to_csv(all_cases_table_path, index=False, encoding="utf-8-sig")

# ---------------------- 2. 合并数据，计算性能指标 ----------------------
compare_list = []
for idx, row in heuristic_df.iterrows():
    filename = row["文件名"]
    # 仅处理【有最优解】的小规模实例
    if filename in optimal_map:
        # 跳过日志错误行和无效行
        if str(row.get("是否有效", "")).lower() != "true":
            continue

        heuristic_size = row["启发式解"]
        heuristic_time = row["运行时间"]
        n_value = row["顶点数"]
        optimal_size = optimal_map[filename]
        brute_time = bruteforce_time_map.get(filename)

        if pd.isna(heuristic_size) or pd.isna(heuristic_time) or pd.isna(n_value):
            continue

        heuristic_size = int(heuristic_size)
        heuristic_time = float(heuristic_time)
        n_value = int(n_value)

        if heuristic_size <= 0 or optimal_size <= 0:
            continue

        # 计算核心性能指标
        approx_ratio = round(heuristic_size / optimal_size, 2)
        is_optimal = 1 if heuristic_size == optimal_size else 0

        compare_list.append({
            "实例名称": filename,
            "顶点数n": n_value,
            "最优解标签数": optimal_size,
            "启发式解标签数": heuristic_size,
            "近似比": approx_ratio,
            "启发式时间(s)": heuristic_time,
            "暴力时间(s)": round(float(brute_time), 6) if brute_time is not None else None,
            "是否命中最优解": is_optimal
        })

# 生成对比数据表
compare_df = pd.DataFrame(compare_list)
comparison_path = os.path.join(SMALL_COMPARE_DIR, "performance_comparison.csv")
compare_df.to_csv(comparison_path, index=False, encoding="utf-8-sig")

# ---------------------- 3. 计算汇总性能 ----------------------
total = len(compare_df)
if total == 0:
    summary = {
        "小规模实例总数": 0,
        "最优解命中数": 0,
        "最优命中率(%)": 0.0,
        "平均近似比": 0.0,
    }
else:
    hit_optimal = int(compare_df["是否命中最优解"].sum())
    avg_approx = float(compare_df["近似比"].mean())

    summary = {
        "小规模实例总数": total,
        "最优解命中数": hit_optimal,
        "最优命中率(%)": round(hit_optimal / total * 100, 2),
        "平均近似比": round(avg_approx, 2),
    }

summary_path = os.path.join(SMALL_COMPARE_DIR, "performance_summary.json")
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=4)

# ---------------------- 4. 绘制性能对比图表（新增部分）----------------------
df = pd.read_csv(comparison_path)
df = df.sort_values(by=["顶点数n", "实例名称"]).reset_index(drop=True)

if df.empty:
    raise RuntimeError("性能对比数据为空，无法绘图。请先运行 main.py 和 src/brute_force.py。")


def save_fig(path: str):
    """统一保存风格，避免图像裁剪。"""
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


if heuristic_valid_df.empty:
    raise RuntimeError("全测试用例日志为空，无法生成蒙特卡洛全量可视化。")

# 图0：全测试用例运行时间折线图
plt.figure(figsize=(12, 5.5))
labels_all = [name.replace("instance_", "i") for name in heuristic_valid_df["文件名"].tolist()]
plt.plot(
    range(len(heuristic_valid_df)),
    heuristic_valid_df["运行时间_num"],
    color="#1F77B4",
    marker="o",
    markersize=3,
    linewidth=1.5,
)
plt.xlabel("测试实例")
plt.ylabel("运行时间 (s)")
plt.title("蒙特卡洛启发式在全测试用例上的运行时间")
plt.xticks(range(len(labels_all)), labels_all, rotation=70, ha="right", fontsize=7)
all_runtime_line_path = os.path.join(ALL_CASES_DIR, "all_cases_runtime_line.png")
save_fig(all_runtime_line_path)

# 图0-2：全测试用例割集大小柱状图
plt.figure(figsize=(12, 5.5))
plt.bar(
    range(len(heuristic_valid_df)),
    heuristic_valid_df["启发式解_num"],
    color="#4C956C",
    edgecolor="#2f2f2f",
    linewidth=0.4,
)
plt.xlabel("测试实例")
plt.ylabel("启发式割集大小")
plt.title("蒙特卡洛启发式在全测试用例上的割集大小")
plt.xticks(range(len(labels_all)), labels_all, rotation=70, ha="right", fontsize=7)
all_cutsize_bar_path = os.path.join(ALL_CASES_DIR, "all_cases_cutsize_bar.png")
save_fig(all_cutsize_bar_path)

# 图0-3：按规模分组的平均运行时间和平均割集大小
group_df = heuristic_valid_df.groupby("顶点数_num", as_index=False).agg(
    平均运行时间=("运行时间_num", "mean"),
    平均割集大小=("启发式解_num", "mean"),
    实例数=("文件名", "count"),
)

plt.figure(figsize=(8.8, 5.2))
ax1 = plt.gca()
ax1.plot(group_df["顶点数_num"], group_df["平均运行时间"], color="#1F77B4", marker="o", label="平均运行时间")
ax1.set_xlabel("顶点数 n")
ax1.set_ylabel("平均运行时间 (s)", color="#1F77B4")
ax1.tick_params(axis="y", labelcolor="#1F77B4")
ax1.xaxis.set_major_locator(MaxNLocator(integer=True))

ax2 = ax1.twinx()
ax2.plot(group_df["顶点数_num"], group_df["平均割集大小"], color="#D2691E", marker="s", label="平均割集大小")
ax2.set_ylabel("平均割集大小", color="#D2691E")
ax2.tick_params(axis="y", labelcolor="#D2691E")

plt.title("按规模分组的蒙特卡洛启发式表现")
group_perf_path = os.path.join(ALL_CASES_DIR, "all_cases_group_performance.png")
save_fig(group_perf_path)

# 图1：最优解 vs 启发式解 大小对比
plt.figure(figsize=(12, 6))
x = range(len(df))
plt.bar(x, df["最优解标签数"], width=0.4, label="最优解", color="#2E86AB")
plt.bar([i+0.4 for i in x], df["启发式解标签数"], width=0.4, label="启发式解", color="#A23B72")
plt.xlabel("测试实例")
plt.ylabel("标签割集大小")
plt.title("启发式解与最优解大小对比")
instance_labels = [name.replace("instance_", "i") for name in df["实例名称"].tolist()]
plt.xticks([i + 0.2 for i in x], instance_labels, rotation=55, ha="right", fontsize=8)
plt.legend()
cut_size_fig_path = os.path.join(SMALL_COMPARE_DIR, "cut_size_compare.png")
save_fig(cut_size_fig_path)

# 图4-2：近似比区间分布图
ratio_values = df["近似比"].astype(float)
ratio_distribution = {
    "1.00": int((ratio_values == 1.0).sum()),
    "(1.0, 1.5]": int(((ratio_values > 1.0) & (ratio_values <= 1.5)).sum()),
    "(1.5, 2.0]": int(((ratio_values > 1.5) & (ratio_values <= 2.0)).sum()),
    "> 2.0": int((ratio_values > 2.0).sum()),
}

plt.figure(figsize=(8.5, 5.2))
bars = plt.bar(
    list(ratio_distribution.keys()),
    list(ratio_distribution.values()),
    color=["#2E8B57", "#4C956C", "#D9923B", "#C44E52"],
    edgecolor="#2f2f2f",
    linewidth=0.6,
)
plt.xlabel("近似比区间")
plt.ylabel("实例数量")
plt.title("小规模实例近似比分布图")
plt.ylim(0, max(ratio_distribution.values()) + 2)
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.15,
        f"{int(height)}",
        ha="center",
        va="bottom",
        fontsize=9,
    )
approx_ratio_dist_path = os.path.join(SMALL_COMPARE_DIR, "approx_ratio_distribution_bar.png")
save_fig(approx_ratio_dist_path)

# 图3：小规模实例双算法运行时间同图对比
runtime_compare_df = df.dropna(subset=["启发式时间(s)", "暴力时间(s)"]).copy()
if not runtime_compare_df.empty:
    plt.figure(figsize=(12, 6))
    x_runtime = range(len(runtime_compare_df))
    width = 0.42
    plt.bar(
        [i - width / 2 for i in x_runtime],
        runtime_compare_df["启发式时间(s)"],
        width=width,
        label="启发式算法",
        color="#1F77B4",
    )
    plt.bar(
        [i + width / 2 for i in x_runtime],
        runtime_compare_df["暴力时间(s)"],
        width=width,
        label="暴力枚举",
        color="#E07A5F",
    )
    labels_runtime = [
        name.replace("instance_", "i")
        for name in runtime_compare_df["实例名称"].tolist()
    ]
    plt.xlabel("测试实例")
    plt.ylabel("运行时间 (s)")
    plt.title("小规模实例双算法运行时间对比")
    plt.xticks(list(x_runtime), labels_runtime, rotation=55, ha="right", fontsize=8)
    plt.legend()
    runtime_dual_compare_path = os.path.join(SMALL_COMPARE_DIR, "runtime_dual_compare_bar.png")
    save_fig(runtime_dual_compare_path)
else:
    runtime_dual_compare_path = "未生成（缺少双算法同实例运行时间）"

# 图2：规模-运行时间散点图（越右越大规模）
plt.figure(figsize=(8.5, 5))
sizes = [40 + 4 * val for val in df["启发式解标签数"]]
plt.scatter(
    df["顶点数n"],
    df["启发式时间(s)"],
    s=sizes,
    c=df["近似比"],
    cmap="YlGnBu",
    alpha=0.85,
    edgecolors="#2f2f2f",
    linewidths=0.5,
)
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
plt.xlabel("顶点数 n")
plt.ylabel("启发式时间 (s)")
plt.title("问题规模与运行时间关系（颜色=近似比，点大小=启发式解）")
plt.colorbar(label="近似比")
runtime_vs_n_path = os.path.join(SMALL_COMPARE_DIR, "runtime_vs_n_scatter.png")
save_fig(runtime_vs_n_path)

# 图4-2：中大规模实例 运行时间-边数m 散点图
mid_large_df = heuristic_valid_df[heuristic_valid_df["顶点数_num"] >= 20].copy()
if not mid_large_df.empty:
    plt.figure(figsize=(8.5, 5))
    sizes_m = [35 + 8 * val for val in mid_large_df["标签数_num"].fillna(0)]
    plt.scatter(
        mid_large_df["边数m_num"],
        mid_large_df["运行时间_num"],
        s=sizes_m,
        c=mid_large_df["顶点数_num"],
        cmap="YlOrRd",
        alpha=0.85,
        edgecolors="#2f2f2f",
        linewidths=0.5,
    )
    plt.xlabel("边数 m")
    plt.ylabel("运行时间 (s)")
    plt.title("中大规模实例运行时间与边数关系（颜色=顶点数n，点大小=标签数q）")
    plt.colorbar(label="顶点数 n")
    runtime_vs_m_path = os.path.join(ALL_CASES_DIR, "runtime_vs_m_scatter.png")
    save_fig(runtime_vs_m_path)
else:
    runtime_vs_m_path = "未生成（中大规模有效实例为空）"

# 图5：命中最优解比例环图
hit_count = int(df["是否命中最优解"].sum())
miss_count = int(len(df) - hit_count)
plt.figure(figsize=(5.8, 5.8))
wedges, texts, autotexts = plt.pie(
    [hit_count, miss_count],
    labels=["命中最优", "未命中"],
    colors=["#2E8B57", "#C44E52"],
    startangle=90,
    counterclock=False,
    autopct="%.1f%%",
    pctdistance=0.78,
    wedgeprops={"width": 0.42, "edgecolor": "white"},
)
for t in autotexts:
    t.set_color("#222222")
plt.title("最优解命中率")
optimal_hit_rate_path = os.path.join(SMALL_COMPARE_DIR, "optimal_hit_rate_donut.png")
save_fig(optimal_hit_rate_path)

# ---------------------- 打印结果 ----------------------
print("===== 启发式算法性能汇总（对比最优解）=====")
for k, v in summary.items():
    print(f"{k}: {v}")
print("\n✅ 已生成文件：")
print(f"1. {comparison_path}  (详细对比表)")
print(f"2. {summary_path}   (性能汇总)")
print(f"3. {cut_size_fig_path}       (解大小对比图)")
print(f"4. {approx_ratio_dist_path}    (近似比分布图)")
print(f"5. {runtime_dual_compare_path}    (双算法运行时间对比图)")
print(f"6. {runtime_vs_n_path}    (规模-时间散点图)")
print(f"7. {optimal_hit_rate_path}    (最优命中率环图)")
print(f"8. {all_cases_table_path}    (全测试用例数据表)")
print(f"9. {all_runtime_line_path}    (全测试用例运行时间图)")
print(f"10. {all_cutsize_bar_path}    (全测试用例割集大小图)")
print(f"11. {group_perf_path}    (按规模分组表现图)")
print(f"12. {runtime_vs_m_path}    (中大规模时间-边数散点图)")