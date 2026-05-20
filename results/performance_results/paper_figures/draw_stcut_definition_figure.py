import os
import matplotlib.pyplot as plt
from matplotlib import font_manager


def configure_fonts() -> None:
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


def draw_stcut_definition_figure(output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), facecolor="white")
    fig.suptitle("标签 s-t 割问题定义示例图", fontsize=20, y=0.98)

    pos = {"s": (0.1, 0.1), "a": (0.5, 0.78), "t": (0.9, 0.1)}
    node_fc = "#F6F1D8"
    node_ec = "#2F2F2F"
    keep_c = "#1f77b4"
    rm_c = "#C44E52"

    def draw_nodes(ax):
        for n, (x, y) in pos.items():
            circle = plt.Circle((x, y), 0.055, facecolor=node_fc, edgecolor=node_ec, linewidth=1.6, zorder=3)
            ax.add_patch(circle)
            ax.text(x, y, n, ha="center", va="center", fontsize=18)

    def draw_edge(ax, u, v, color, ls="-", lw=3.0, alpha=1.0):
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        ax.plot([x1, x2], [y1, y2], color=color, linestyle=ls, linewidth=lw, alpha=alpha, zorder=1)

    def label_edge(ax, u, v, txt, color="#111111", offset=(0, 0)):
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        mx, my = (x1 + x2) / 2 + offset[0], (y1 + y2) / 2 + offset[1]
        ax.text(mx, my, txt, fontsize=16, color=color, ha="center", va="center")

    def base_setup(ax, title):
        ax.set_title(title, fontsize=16, pad=10)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")

    ax = axes[0, 0]
    base_setup(ax, "(a) 原始带标签图")
    draw_nodes(ax)
    draw_edge(ax, "s", "a", keep_c)
    draw_edge(ax, "a", "t", keep_c)
    draw_edge(ax, "s", "t", keep_c)
    label_edge(ax, "s", "a", "$\\ell_1$", offset=(-0.02, 0.04))
    label_edge(ax, "a", "t", "$\\ell_1$", offset=(0.02, 0.04))
    label_edge(ax, "s", "t", "$\\ell_2$", offset=(0, 0.03))
    ax.text(0.5, -0.08, "$V=\\{s,a,t\\},\\ E=\\{(s,a,\\ell_1),(a,t,\\ell_1),(s,t,\\ell_2)\\}$", fontsize=13, ha="center")

    ax = axes[0, 1]
    base_setup(ax, "(b) 删除标签 $\\ell_1$")
    draw_nodes(ax)
    draw_edge(ax, "s", "a", rm_c, ls="--", lw=2.8)
    draw_edge(ax, "a", "t", rm_c, ls="--", lw=2.8)
    draw_edge(ax, "s", "t", keep_c)
    label_edge(ax, "s", "a", "$\\ell_1$（删）", color=rm_c, offset=(-0.02, 0.045))
    label_edge(ax, "a", "t", "$\\ell_1$（删）", color=rm_c, offset=(0.02, 0.045))
    label_edge(ax, "s", "t", "$\\ell_2$", offset=(0, 0.03))
    ax.text(0.5, -0.08, "仅剩边 $(s,t,\\ell_2)$，$s$ 与 $t$ 仍连通", fontsize=13.5, ha="center")

    ax = axes[1, 0]
    base_setup(ax, "(c) 删除标签 $\\ell_2$")
    draw_nodes(ax)
    draw_edge(ax, "s", "a", keep_c)
    draw_edge(ax, "a", "t", keep_c)
    draw_edge(ax, "s", "t", rm_c, ls="--", lw=2.8)
    label_edge(ax, "s", "a", "$\\ell_1$", offset=(-0.02, 0.04))
    label_edge(ax, "a", "t", "$\\ell_1$", offset=(0.02, 0.04))
    label_edge(ax, "s", "t", "$\\ell_2$（删）", color=rm_c, offset=(0, 0.03))
    ax.text(0.5, -0.08, "仍有路径 $s \\to a \\to t$（标签 $\\ell_1$）", fontsize=13.5, ha="center")

    ax = axes[1, 1]
    base_setup(ax, "(d) 删除标签集合 $\\{\\ell_1,\\ell_2\\}$")
    draw_nodes(ax)
    draw_edge(ax, "s", "a", rm_c, ls="--", lw=2.8)
    draw_edge(ax, "a", "t", rm_c, ls="--", lw=2.8)
    draw_edge(ax, "s", "t", rm_c, ls="--", lw=2.8)
    label_edge(ax, "s", "a", "$\\ell_1$（删）", color=rm_c, offset=(-0.02, 0.045))
    label_edge(ax, "a", "t", "$\\ell_1$（删）", color=rm_c, offset=(0.02, 0.045))
    label_edge(ax, "s", "t", "$\\ell_2$（删）", color=rm_c, offset=(0, 0.03))
    ax.text(0.5, -0.08, "$s$ 与 $t$ 断连，故最优解 $C^*=\\{\\ell_1,\\ell_2\\}$，$|C^*|=2$", fontsize=13.5, ha="center")

    fig.tight_layout(rect=[0, 0, 1, 0.95])
    base = os.path.join(output_dir, "stcut_definition_example_polished")
    fig.savefig(base + ".png", dpi=400, bbox_inches="tight", facecolor="white")
    fig.savefig(base + ".svg", bbox_inches="tight", facecolor="white")


if __name__ == "__main__":
    configure_fonts()
    draw_stcut_definition_figure(output_dir=os.path.dirname(os.path.abspath(__file__)))
