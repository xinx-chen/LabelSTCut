# LabelSTCut

标签 s-t 割问题的蒙特卡洛启发式算法实现、测试与性能分析框架。

## 项目简介

本项目实现了解决**标签 s-t 割问题**的蒙特卡洛启发式算法，包括：
- **蒙特卡洛采样启发式**：快速求解大规模实例
- **枚举求解**：小规模实例的最优解获取  
- **性能分析**：近似比、运行时间、可视化统计

## 核心特性

- 完整的图论数据结构与标签管理
- 多种采样策略（MSG、MSS）
- 小规模最优解枚举与大规模启发式求解
- 自动生成标准化测试实例（100+规模）
- 性能指标统计与可视化

## 项目结构

```
LabelSTCut/
├── src/                        # 核心模块
│   ├── __init__.py            # 导出主接口
│   ├── graph_base.py          # 标签图数据结构
│   ├── brute_force.py         # 暴力枚举求解器
│   ├── heuristic_main.py      # 蒙特卡洛启发式主函数
│   ├── msg_sampler.py         # MSG 采样策略
│   ├── mss_sampler.py         # MSS 采样策略
│   ├── utils.py               # 工具函数
│   └── config.py              # 共享配置
├── test_instances/            # 生成的测试实例（JSON + TXT）
│   └── plots/                 # 实例可视化图表（自动生成）
├── results/                   # 运行结果输出（忽略）
│   ├── algorithm_results/     # 算法测试日志
│   ├── bruteforce_results/    # 暴力枚举结果
│   └── performance_results/   # 性能对比与图表
├── main.py                    # 主测试脚本
├── generate_test_instances.py # 生成测试实例脚本
├── performance_analysis.py    # 性能分析脚本
├── brute_force_visualize.py   # 暴力枚举可视化脚本
├── MSGonly.py                 # MSG 单独测试
├── requirements.txt           # 依赖清单
├── .gitignore                 # Git 忽略规则
└── README.md                  # 本文件
```

## 快速开始

### 1. 环境配置

克隆并进入项目：
```bash
git clone https://github.com/xinx-chen/LabelSTCut.git
cd LabelSTCut
```

安装依赖：
```bash
pip install -r requirements.txt
```

或使用虚拟环境：
```bash
python3 -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
```

### 2. 生成测试实例

```bash
python generate_test_instances.py
```

生成 100 个标准化测试实例（5 ≤ n ≤ 60），保存为 JSON 和 TXT 格式。

### 3. 运行算法测试

```bash
python main.py
```

- 对小规模实例（n ≤ 15）执行**枚举**求最优解
- 对所有实例运行**蒙特卡洛启发式**求解
- 输出日志到 `results/algorithm_results/test_log.txt`

### 4. 性能分析与可视化

```bash
python performance_analysis.py
```

生成性能对比报告与图表（需先运行 `main.py`）：
- 小规模对比：最优解命中率、近似比、运行时间
- 全规模统计：不同规模下的运行时间分布
- 输出路径：`results/performance_results/`

## 关键文件说明

### 源码模块 (`src/`)

| 文件 | 功能 |
|------|------|
| `graph_base.py` | 标签图数据结构（LabeledGraph 类） |
| `brute_force.py` | 暴力枚举最优割求解 |
| `heuristic_main.py` | 蒙特卡洛启发式主算法 |
| `msg_sampler.py` | MSG（多步骤贪心）采样 |
| `mss_sampler.py` | MSS（多步骤随机）采样 |
| `utils.py` | 工具函数（图操作、验证等） |
| `config.py` | 全局配置（阈值、参数） |

### 主脚本

| 脚本 | 用途 |
|------|------|
| `main.py` | 核心测试：读取实例 → 运行算法 → 输出日志 |
| `generate_test_instances.py` | 生成 100 个标准化测试实例 |
| `performance_analysis.py` | 对比分析 & 可视化（CSV、图表、JSON） |
| `brute_force_visualize.py` | 暴力枚举单独可视化 |
| `MSGonly.py` | MSG 采样单独测试 |

### 配置参数 (`main.py`)

```python
DEBUG_MODE = True          # 详细输出模式
BATCH_TEST = True          # 批量测试所有实例
MAX_SCORE = 120            # 蒙特卡洛启发式的最大迭代轮次
RANDOM_SEED = 42           # 固定随机种子（可复现）
SMALL_SCALE_THRESHOLD = 15 # 执行暴力枚举的阈值
```

## 输出结果说明

运行测试后，结果存储在 `results/` 目录（忽略）：

```
results/
├── algorithm_results/
│   ├── test_log.txt                    # 主测试日志（CSV格式）
│   └── brute_force_optimal_results.json # 暴力枚举结果
├── bruteforce_results/
│   └── brute_force_results_detailed.csv # 详细暴力枚举表
└── performance_results/
    ├── small_scale_comparison/
    │   ├── performance_comparison.csv   # 小规模对比表
    │   ├── performance_summary.json     # 汇总统计
    │   └── *.png                       # 对比图表
    └── all_cases_heuristic/
        ├── heuristic_all_cases.csv      # 全规模结果表
        └── *.png                       # 性能可视化
```

## 技术细节

### 算法概述

**标签 s-t 割问题**：给定标签图 G 和源汇对 (s,t)，选择最小数量的标签使其移除后 s 与 t 不连通。

**蒙特卡洛启发式**：
1. 随机采样移除边/标签
2. 检查 s-t 连通性
3. 迭代改进割的质量
4. 返回最优割集

### 可复现性

- 使用固定的 `RANDOM_SEED = 42`
- 避免 Python `hash()` 的随机化（改用 `zlib.crc32`）
- 所有算法结果与论文对应

## 依赖

详见 `requirements.txt`：
- Python 3.7+
- `networkx`：图论库
- `pandas`：数据处理
- `matplotlib`：可视化


