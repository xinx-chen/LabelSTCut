import random
import json
import os
import networkx as nx
import matplotlib.pyplot as plt

# ===================== 固定随机种子 =====================
random.seed(50)
# 设置matplotlib随机种子确保绘图一致性
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']  # 确保标签显示正常
plt.rcParams['axes.unicode_minus'] = False
# ===================== 100个测试实例参数设计（学术标准版，增强可信度） =====================
INSTANCES = [
    # 1. 小规模：n=5~15（枚举最优解，35个，核心性能对比基准）
    {"n":5, "p":0.1, "q":2, "name":"instance_01_n5_p0.1_q2"},
    {"n":5, "p":0.3, "q":2, "name":"instance_02_n5_p0.3_q2"},
    {"n":5, "p":0.5, "q":3, "name":"instance_03_n5_p0.5_q3"},
    {"n":5, "p":0.7, "q":2, "name":"instance_04_n5_p0.7_q2"},
    {"n":5, "p":0.9, "q":5, "name":"instance_05_n5_p0.9_q5"},
    {"n":5, "p":0.2, "q":3, "name":"instance_06_n5_p0.2_q3"},
    {"n":5, "p":0.4, "q":4, "name":"instance_07_n5_p0.4_q4"},
    {"n":5, "p":0.6, "q":3, "name":"instance_08_n5_p0.6_q3"},

    {"n":8, "p":0.1, "q":3, "name":"instance_09_n8_p0.1_q3"},
    {"n":8, "p":0.3, "q":4, "name":"instance_10_n8_p0.3_q4"},
    {"n":8, "p":0.4, "q":4, "name":"instance_11_n8_p0.4_q4"},
    {"n":8, "p":0.5, "q":5, "name":"instance_12_n8_p0.5_q5"},
    {"n":8, "p":0.6, "q":5, "name":"instance_13_n8_p0.6_q5"},
    {"n":8, "p":0.7, "q":6, "name":"instance_14_n8_p0.7_q6"},
    {"n":8, "p":0.8, "q":8, "name":"instance_15_n8_p0.8_q8"},
    {"n":8, "p":0.9, "q":7, "name":"instance_16_n8_p0.9_q7"},

    {"n":10, "p":0.2, "q":5, "name":"instance_17_n10_p0.2_q5"},
    {"n":10, "p":0.3, "q":6, "name":"instance_18_n10_p0.3_q6"},
    {"n":10, "p":0.4, "q":6, "name":"instance_19_n10_p0.4_q6"},
    {"n":10, "p":0.5, "q":7, "name":"instance_20_n10_p0.5_q7"},
    {"n":10, "p":0.6, "q":8, "name":"instance_21_n10_p0.6_q8"},
    {"n":10, "p":0.7, "q":9, "name":"instance_22_n10_p0.7_q9"},
    {"n":10, "p":0.8, "q":8, "name":"instance_23_n10_p0.8_q8"},

    {"n":12, "p":0.2, "q":4, "name":"instance_24_n12_p0.2_q4"},
    {"n":12, "p":0.4, "q":6, "name":"instance_25_n12_p0.4_q6"},
    {"n":12, "p":0.5, "q":7, "name":"instance_26_n12_p0.5_q7"},
    {"n":12, "p":0.6, "q":8, "name":"instance_27_n12_p0.6_q8"},
    {"n":12, "p":0.7, "q":6, "name":"instance_28_n12_p0.7_q6"},
    {"n":12, "p":0.8, "q":9, "name":"instance_29_n12_p0.8_q9"},
    {"n":12, "p":0.9, "q":10, "name":"instance_30_n12_p0.9_q10"},

    {"n":15, "p":0.2, "q":5, "name":"instance_31_n15_p0.2_q5"},
    {"n":15, "p":0.4, "q":7, "name":"instance_32_n15_p0.4_q7"},
    {"n":15, "p":0.5, "q":8, "name":"instance_33_n15_p0.5_q8"},
    {"n":15, "p":0.6, "q":8, "name":"instance_34_n15_p0.6_q8"},
    {"n":15, "p":0.8, "q":8, "name":"instance_35_n15_p0.8_q8"},

    # 2. 中规模：n=20~40（算法性能测试，35个）
    {"n":20, "p":0.1, "q":10, "name":"instance_36_n20_p0.1_q10"},
    {"n":20, "p":0.2, "q":10, "name":"instance_37_n20_p0.2_q10"},
    {"n":20, "p":0.3, "q":12, "name":"instance_38_n20_p0.3_q12"},
    {"n":20, "p":0.4, "q":13, "name":"instance_39_n20_p0.4_q13"},
    {"n":20, "p":0.5, "q":15, "name":"instance_40_n20_p0.5_q15"},
    {"n":20, "p":0.6, "q":16, "name":"instance_41_n20_p0.6_q16"},
    {"n":20, "p":0.7, "q":18, "name":"instance_42_n20_p0.7_q18"},
    {"n":20, "p":0.8, "q":20, "name":"instance_43_n20_p0.8_q20"},
    {"n":20, "p":0.9, "q":25, "name":"instance_44_n20_p0.9_q25"},

    {"n":25, "p":0.1, "q":12, "name":"instance_45_n25_p0.1_q12"},
    {"n":25, "p":0.3, "q":14, "name":"instance_46_n25_p0.3_q14"},
    {"n":25, "p":0.5, "q":16, "name":"instance_47_n25_p0.5_q16"},
    {"n":25, "p":0.7, "q":18, "name":"instance_48_n25_p0.7_q18"},
    {"n":25, "p":0.9, "q":22, "name":"instance_49_n25_p0.9_q22"},

    {"n":30, "p":0.1, "q":15, "name":"instance_50_n30_p0.1_q15"},
    {"n":30, "p":0.2, "q":16, "name":"instance_51_n30_p0.2_q16"},
    {"n":30, "p":0.3, "q":18, "name":"instance_52_n30_p0.3_q18"},
    {"n":30, "p":0.4, "q":19, "name":"instance_53_n30_p0.4_q19"},
    {"n":30, "p":0.5, "q":20, "name":"instance_54_n30_p0.5_q20"},
    {"n":30, "p":0.6, "q":21, "name":"instance_55_n30_p0.6_q21"},
    {"n":30, "p":0.7, "q":22, "name":"instance_56_n30_p0.7_q22"},
    {"n":30, "p":0.8, "q":25, "name":"instance_57_n30_p0.8_q25"},
    {"n":30, "p":0.9, "q":30, "name":"instance_58_n30_p0.9_q30"},

    {"n":35, "p":0.2, "q":18, "name":"instance_59_n35_p0.2_q18"},
    {"n":35, "p":0.4, "q":20, "name":"instance_60_n35_p0.4_q20"},
    {"n":35, "p":0.6, "q":22, "name":"instance_61_n35_p0.6_q22"},
    {"n":35, "p":0.8, "q":26, "name":"instance_62_n35_p0.8_q26"},

    {"n":40, "p":0.1, "q":20, "name":"instance_63_n40_p0.1_q20"},
    {"n":40, "p":0.3, "q":22, "name":"instance_64_n40_p0.3_q22"},
    {"n":40, "p":0.5, "q":25, "name":"instance_65_n40_p0.5_q25"},
    {"n":40, "p":0.7, "q":27, "name":"instance_66_n40_p0.7_q27"},
    {"n":40, "p":0.9, "q":30, "name":"instance_67_n40_p0.9_q30"},
    {"n":40, "p":0.4, "q":25, "name":"instance_68_n40_p0.4_q25"},
    {"n":40, "p":0.6, "q":28, "name":"instance_69_n40_p0.6_q28"},
    {"n":40, "p":0.8, "q":29, "name":"instance_70_n40_p0.8_q29"},

    # 3. 大规模：n=45~60（算法鲁棒性测试，30个）
    {"n":45, "p":0.1, "q":22, "name":"instance_71_n45_p0.1_q22"},
    {"n":45, "p":0.2, "q":24, "name":"instance_72_n45_p0.2_q24"},
    {"n":45, "p":0.3, "q":25, "name":"instance_73_n45_p0.3_q25"},
    {"n":45, "p":0.4, "q":26, "name":"instance_74_n45_p0.4_q26"},
    {"n":45, "p":0.5, "q":28, "name":"instance_75_n45_p0.5_q28"},
    {"n":45, "p":0.6, "q":30, "name":"instance_76_n45_p0.6_q30"},
    {"n":45, "p":0.7, "q":32, "name":"instance_77_n45_p0.7_q32"},
    {"n":45, "p":0.8, "q":34, "name":"instance_78_n45_p0.8_q34"},
    {"n":45, "p":0.9, "q":36, "name":"instance_79_n45_p0.9_q36"},

    {"n":50, "p":0.1, "q":25, "name":"instance_80_n50_p0.1_q25"},
    {"n":50, "p":0.2, "q":25, "name":"instance_81_n50_p0.2_q25"},
    {"n":50, "p":0.3, "q":26, "name":"instance_82_n50_p0.3_q26"},
    {"n":50, "p":0.4, "q":28, "name":"instance_83_n50_p0.4_q28"},
    {"n":50, "p":0.5, "q":30, "name":"instance_84_n50_p0.5_q30"},
    {"n":50, "p":0.6, "q":32, "name":"instance_85_n50_p0.6_q32"},
    {"n":50, "p":0.7, "q":34, "name":"instance_86_n50_p0.7_q34"},
    {"n":50, "p":0.8, "q":36, "name":"instance_87_n50_p0.8_q36"},
    {"n":50, "p":0.9, "q":38, "name":"instance_88_n50_p0.9_q38"},

    {"n":55, "p":0.2, "q":28, "name":"instance_89_n55_p0.2_q28"},
    {"n":55, "p":0.4, "q":30, "name":"instance_90_n55_p0.4_q30"},
    {"n":55, "p":0.6, "q":33, "name":"instance_91_n55_p0.6_q33"},
    {"n":55, "p":0.8, "q":36, "name":"instance_92_n55_p0.8_q36"},

    {"n":60, "p":0.1, "q":30, "name":"instance_93_n60_p0.1_q30"},
    {"n":60, "p":0.2, "q":31, "name":"instance_94_n60_p0.2_q31"},
    {"n":60, "p":0.3, "q":32, "name":"instance_95_n60_p0.3_q32"},
    {"n":60, "p":0.4, "q":34, "name":"instance_96_n60_p0.4_q34"},
    {"n":60, "p":0.5, "q":35, "name":"instance_97_n60_p0.5_q35"},
    {"n":60, "p":0.6, "q":36, "name":"instance_98_n60_p0.6_q36"},
    {"n":60, "p":0.7, "q":38, "name":"instance_99_n60_p0.7_q38"},
    {"n":60, "p":0.8, "q":40, "name":"instance_100_n60_p0.8_q40"},
]

# ===================== 生成 G[n,p] 无向图 =====================
def generate_gnp_graph(n, p):
    edges = []
    # 无向图：u < v，避免重复边
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < p:
                edges.append((u, v))
    return edges

# ===================== 为边随机分配标签 =====================
def assign_labels(edges, q):
    labeled_edges = []
    for u, v in edges:
        label = random.randint(0, q - 1)
        labeled_edges.append((u, v, label))
    return labeled_edges


def ensure_st_connected(labeled_edges, n, q, s=0, t=None):
    """确保实例中 s 与 t 可达；若不可达则补一条桥接边。"""
    if t is None:
        t = n - 1

    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from((u, v) for u, v, _ in labeled_edges)

    if nx.has_path(G, s, t):
        return labeled_edges

    bridge_label = random.randint(0, q - 1)
    labeled_edges.append((s, t, bridge_label))
    return labeled_edges

# ===================== 绘制并保存图（新增边标签展示） =====================
def plot_instance(params, labeled_edges):
    n = params["n"]
    name = params["name"]
    s = 0
    t = n - 1
    
    # 创建无向图
    G = nx.Graph()
    G.add_nodes_from(range(n))
    # 添加带标签的边
    edge_list = [(u, v) for u, v, l in labeled_edges]
    G.add_edges_from(edge_list)
    # 构建边标签字典 { (u,v): label }
    edge_labels = {(u, v): str(l) for u, v, l in labeled_edges}
    
    # 根据图的规模选择布局
    if n <= 20:
        pos = nx.spring_layout(G, seed=42, k=2)  # 小规模用spring布局，更美观
    elif n <= 50:
        pos = nx.spring_layout(G, seed=42, k=1.5)
    else:
        pos = nx.spring_layout(G, seed=42, k=1.2)  # 大规模减小节点间距
    
    # 创建画布
    fig_size = min(15, max(8, n/5))  # 根据节点数自适应画布大小
    plt.figure(figsize=(fig_size, fig_size))
    
    # 绘制节点
    # 普通节点
    normal_nodes = [node for node in G.nodes() if node != s and node != t]
    nx.draw_networkx_nodes(G, pos, nodelist=normal_nodes, 
                           node_color='lightblue', node_size=500, alpha=0.8)
    # 源节点s(红色)和汇节点t(绿色)
    nx.draw_networkx_nodes(G, pos, nodelist=[s], 
                           node_color='red', node_size=700, alpha=0.9, node_shape='s')  # 方形
    nx.draw_networkx_nodes(G, pos, nodelist=[t], 
                           node_color='green', node_size=700, alpha=0.9, node_shape='^')  # 三角形
    
    # 绘制边
    nx.draw_networkx_edges(G, pos, edgelist=edge_list, alpha=0.6, width=1.0)
    
    # 绘制节点标签
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    # 绘制边标签（核心新增：展示每条边的标签）
    nx.draw_networkx_edge_labels(
        G, pos, 
        edge_labels=edge_labels,
        font_size=8,  # 适配小规模图的标签大小
        font_color='darkred',
        bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.7)  # 标签背景，避免遮挡
    )
    
    # 添加图例和标题
    plt.title(f'Test Instance: {name}\nn={n}, |E|={len(edge_list)}', fontsize=14, pad=20)
    plt.legend(
        handles=[
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', markersize=10, label='Normal Node'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='red', markersize=10, label=f'Source (s={s})'),
            plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='green', markersize=10, label=f'Target (t={t})'),
            plt.Line2D([0], [0], color='darkred', linewidth=1, label='Edge Label')
        ],
        loc='upper right',
        frameon=True
    )
    
    # 调整布局并保存
    plt.tight_layout()
    plt.axis('off')  # 关闭坐标轴
    os.makedirs("test_instances/plots", exist_ok=True)
    plt.savefig(f"test_instances/plots/{name}.png", dpi=150, bbox_inches='tight')
    plt.close()  # 关闭画布释放内存

# ===================== 保存为 TXT + JSON 文件 =====================
def save_instance(params):
    n = params["n"]
    p = params["p"]
    q = params["q"]
    name = params["name"]
    s = 0
    t = n - 1

    # 生成图和标签
    edges = generate_gnp_graph(n, p)
    labeled_edges = assign_labels(edges, q)
    labeled_edges = ensure_st_connected(labeled_edges, n, q, s=s, t=t)
    m = len(labeled_edges)
    vertices = list(range(n))
    labels = list(range(q))

    # 创建输出文件夹
    os.makedirs("test_instances", exist_ok=True)

    # 1. 保存TXT格式（算法直接读取）
    with open(f"test_instances/{name}.txt", "w", encoding="utf-8") as f:
        f.write(f"# 核心参数\n")
        f.write(f"n: {n}\n")
        f.write(f"m: {m}\n")
        f.write(f"q: {q}\n")
        f.write(f"p: {p}\n")
        f.write(f"s: {s}\n")
        f.write(f"t: {t}\n\n")
        f.write(f"# 顶点集 V\n")
        f.write(f"V: {' '.join(map(str, vertices))}\n\n")
        f.write(f"# 标签集 L\n")
        f.write(f"L: {' '.join(map(str, labels))}\n\n")
        f.write(f"# 边集 E (u v label)\n")
        f.write(f"E:\n")
        for u, v, l in labeled_edges:
            f.write(f"{u} {v} {l}\n")

    # 2. 保存JSON格式（论文展示/数据归档）
    json_data = {
        "instance_name": name,
        "parameters": {"n": n, "m": m, "q": q, "p": p, "s": s, "t": t},
        "vertices": vertices,
        "labels": labels,
        "edges": labeled_edges
    }
    with open(f"test_instances/{name}.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    # 3. 绘制并保存图形（含边标签）
    plot_instance(params, labeled_edges)

# ===================== 主函数：生成所有实例 =====================
if __name__ == "__main__":
    print("正在生成 G[n,p] 测试实例...")
    for idx, params in enumerate(INSTANCES):
        save_instance(params)
        print(f"生成完成：{params['name']} (包含TXT/JSON/PNG文件)")
    print("\n全部100个测试实例已生成完毕！")
    print("文件保存位置：")
    print("- TXT/JSON文件: test_instances/")
    print("- 可视化图片: test_instances/plots/")