# 电商销售数据分析程序

一个基于 Python 3.9 的电商销售数据分析工具，支持数据生成、处理、可视化和 PDF 报告生成。

## 功能特性

- **数据生成**: 自动生成符合真实业务规律的销售数据（300条记录）
- **数据处理**: 使用 Polars 进行高效数据分析
- **数据可视化**: 使用 Plotly 生成交互式图表
  - 日销售额柱状图
  - 品类销售占比饼图（Top4 + 其他）
- **PDF报告**: 生成专业的数据分析报告，包含图表和文字说明

## 项目结构

```
.
├── data/                   # 存放测试数据（CSV格式）
│   └── sales_data_2026_05.csv
├── output/                 # 存放生成的PDF报告
│   └── sales_report_2026_05.pdf
├── src/                    # 核心代码目录
│   ├── data_generator.py   # 数据生成模块
│   ├── data_processor.py   # 数据处理模块（Polars）
│   ├── visualizer.py       # 可视化模块（Plotly）
│   └── report_generator.py # PDF报告生成模块
├── main.py                 # 主入口文件
└── README.md              # 项目说明文档
```

## 数据字段说明

销售数据包含以下字段：

| 字段名 | 说明 | 示例 |
|--------|------|------|
| 订单ID | 唯一订单标识 | ORD20260420000001 |
| 用户ID | 唯一用户标识 | U12345 |
| 下单时间 | 精确到分钟 | 2026-05-15 14:30 |
| 商品品类 | 8种品类之一 | 手机数码 |
| 单价 | 商品单价（元） | 2999.00 |
| 数量 | 购买数量 | 2 |
| 总价 | 订单总价（元） | 5998.00 |

### 商品品类

1. 手机数码
2. 家用电器
3. 服装鞋包
4. 食品生鲜
5. 美妆个护
6. 家居家装
7. 母婴用品
8. 运动户外

## 环境要求

- Python 3.9+
- 依赖包：
  - polars
  - plotly
  - kaleido
  - reportlab

## 安装依赖

```bash
pip install polars plotly kaleido reportlab
```

## 使用方法

### 快速开始

生成测试数据并进行完整分析：

```bash
python main.py
```

### 命令行参数

```bash
# 指定年月生成数据
python main.py --year 2026 --month 5

# 使用已有数据文件
python main.py --no-generate --data data/my_data.csv

# 指定输出路径
python main.py --output output/my_report.pdf

# 查看帮助
python main.py --help
```

### 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--data` | `-d` | 输入数据文件路径 | data/sales_data_2026_05.csv |
| `--output` | `-o` | 输出PDF报告路径 | output/sales_report_2026_05.pdf |
| `--year` | `-y` | 数据年份 | 2026 |
| `--month` | `-m` | 数据月份 | 5 |
| `--no-generate` | - | 不生成测试数据 | False |

## 数据特点

生成的测试数据考虑了以下真实业务规律：

1. **时间分布**: 订单时间集中在黄金时段（10-12点、14-16点、20-22点）
2. **品类价格**: 不同品类有合理的价格区间
3. **购买数量**: 不同品类的购买数量符合消费习惯
4. **随机性**: 使用随机种子保证可重复性

## 报告内容

生成的PDF报告包含以下内容：

### 第一页：每日销售额趋势分析
- 日销售额柱状图
- 趋势分析和关键发现
- 核心指标说明

### 第二页：商品品类销售占比分析
- 品类销售占比饼图（Top4 + 其他）
- 品类表现分析
- 核心指标汇总表格
- 总结与建议

## 模块说明

### data_generator.py

销售数据生成器，支持：
- 生成指定数量的销售记录
- 模拟黄金时段订单分布
- 各品类合理的价格和数量范围
- 导出为CSV格式

### data_processor.py

数据处理模块，使用 Polars 实现：
- 加载CSV数据
- 按天统计销售额
- 按品类统计销售占比
- 汇总统计信息计算

### visualizer.py

可视化模块，使用 Plotly 实现：
- 日销售额柱状图
- 品类销售占比饼图
- 支持自定义主题和配色

### report_generator.py

PDF报告生成器，使用 ReportLab 实现：
- 多页报告布局
- 图表和文字混排
- 中文字体支持
- 表格样式美化

## 示例输出

运行程序后，将在 `output/` 目录下生成PDF报告，包含：

1. **日销售额柱状图**: 展示2026年5月每日销售趋势
2. **品类占比饼图**: 展示销售额前4名品类分布
3. **数据分析文字**: 详细的数据解读和业务建议
4. **汇总表格**: 核心指标一览

## 重复运行

程序支持重复运行，会直接覆盖已有的PDF报告文件，无需手动删除。

## 技术栈

- **数据处理**: [Polars](https://www.pola.rs/) - 高性能DataFrame库
- **可视化**: [Plotly](https://plotly.com/python/) - 交互式图表库
- **PDF生成**: [ReportLab](https://www.reportlab.com/) - PDF文档生成库
- **图表导出**: [Kaleido](https://github.com/plotly/Kaleido) - Plotly静态图片导出

## 许可证

MIT License

## 作者

AI Assistant
