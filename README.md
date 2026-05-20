# LabelSTCut

标签 s-t 割问题的蒙特卡洛启发式算法实现与实验代码。

## 快速开始

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 生成测试实例

```bash
python generate_test_instances.py
```

3. 运行算法

```bash
python main.py
```

4. 生成性能分析结果

```bash
python performance_analysis.py
```

## 目录说明

- `src/`：核心算法实现
- `test_instances/`：测试实例
- `results/`：运行结果与图表

## 说明

默认会输出到 `results/` 目录下，包含算法日志、暴力枚举结果和性能统计图表。
