#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商销售数据分析程序

功能：
1. 生成/加载销售数据
2. 数据分析处理（Polars）
3. 数据可视化（Plotly）
4. 生成PDF分析报告

作者：AI Assistant
日期：2026-04-20
"""

import os
import sys
import argparse
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_generator import generate_test_data
from data_processor import SalesDataProcessor
from visualizer import SalesVisualizer
from report_generator import PDFReportGenerator


def ensure_directories():
    """确保必要的目录存在"""
    dirs = ['data', 'output', 'src']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)


def run_analysis(data_path: str = None, output_path: str = None, 
                generate_data: bool = True, year: int = 2026, month: int = 5):
    """
    运行完整的销售数据分析流程
    
    Args:
        data_path: 数据文件路径，如果为None则使用默认路径
        output_path: 输出PDF路径，如果为None则使用默认路径
        generate_data: 是否生成测试数据
        year: 数据年份
        month: 数据月份
    """
    print("=" * 60)
    print("电商销售数据分析程序")
    print("=" * 60)
    
    # 确保目录存在
    ensure_directories()
    
    # 设置默认路径
    if data_path is None:
        data_path = f"data/sales_data_{year}_{month:02d}.csv"
    if output_path is None:
        output_path = f"output/sales_report_{year}_{month:02d}.pdf"
    
    # 步骤1: 生成测试数据
    if generate_data:
        print("\n[步骤1/4] 正在生成测试数据...")
        data_path = generate_test_data(
            output_path=data_path,
            count=300,
            year=year,
            month=month
        )
    else:
        print(f"\n[步骤1/4] 使用现有数据: {data_path}")
    
    # 检查数据文件是否存在
    if not os.path.exists(data_path):
        print(f"错误: 数据文件不存在: {data_path}")
        return False
    
    # 步骤2: 数据处理
    print("\n[步骤2/4] 正在处理数据...")
    processor = SalesDataProcessor(data_path)
    
    # 获取统计数据
    daily_sales = processor.get_daily_sales()
    top_categories, others = processor.get_category_sales(top_n=4)
    stats = processor.get_summary_stats()
    
    print(f"  - 数据记录数: {stats['总订单数']}")
    print(f"  - 总销售额: ¥{stats['总销售额']:,.2f}")
    print(f"  - 独立用户数: {stats['独立用户数']}")
    print(f"  - 平均客单价: ¥{stats['平均客单价']:,.2f}")
    
    # 步骤3: 生成可视化图表
    print("\n[步骤3/4] 正在生成可视化图表...")
    visualizer = SalesVisualizer()
    
    daily_chart = visualizer.create_daily_sales_chart(daily_sales)
    pie_chart = visualizer.create_category_pie_chart(top_categories, others)
    
    print("  - 日销售额柱状图: 已生成")
    print("  - 品类占比饼图: 已生成")
    
    # 步骤4: 生成PDF报告
    print("\n[步骤4/4] 正在生成PDF报告...")
    
    # 如果PDF已存在，直接覆盖
    if os.path.exists(output_path):
        print(f"  - 检测到已有报告，将覆盖: {output_path}")
    
    generator = PDFReportGenerator(output_path)
    generator.generate_report(
        daily_chart=daily_chart,
        pie_chart=pie_chart,
        stats=stats,
        report_title=f"{year}年{month}月电商销售数据分析报告"
    )
    
    print("\n" + "=" * 60)
    print("分析完成!")
    print(f"数据文件: {os.path.abspath(data_path)}")
    print(f"报告文件: {os.path.abspath(output_path)}")
    print("=" * 60)
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='电商销售数据分析程序',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                          # 生成数据并分析（默认2026年5月）
  python main.py --year 2026 --month 5    # 指定年月
  python main.py --no-generate --data data/existing.csv  # 使用已有数据
        """
    )
    
    parser.add_argument('--data', '-d', type=str, default=None,
                       help='输入数据文件路径（CSV格式）')
    parser.add_argument('--output', '-o', type=str, default=None,
                       help='输出PDF报告路径')
    parser.add_argument('--year', '-y', type=int, default=2026,
                       help='数据年份（默认: 2026）')
    parser.add_argument('--month', '-m', type=int, default=5,
                       help='数据月份（默认: 5）')
    parser.add_argument('--no-generate', action='store_true',
                       help='不生成测试数据，使用已有数据文件')
    
    args = parser.parse_args()
    
    try:
        success = run_analysis(
            data_path=args.data,
            output_path=args.output,
            generate_data=not args.no_generate,
            year=args.year,
            month=args.month
        )
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
