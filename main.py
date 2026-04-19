#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from src.data_generator import generate_sales_data, save_sales_data
from src.data_processor import (
    load_sales_data,
    aggregate_daily_sales,
    aggregate_category_sales,
    get_top_categories_with_other,
    get_basic_statistics
)
from src.visualizer import (
    create_daily_sales_chart,
    create_category_pie_chart,
    get_chart_as_image
)
from src.pdf_generator import create_pdf_report

def main():
    print("=" * 60)
    print("E-Commerce Sales Data Analysis System")
    print("=" * 60)
    
    data_path = Path("data/sales_data_202605.csv")
    pdf_path = Path("output/sales_analysis_report.pdf")
    
    data_path.parent.mkdir(exist_ok=True)
    pdf_path.parent.mkdir(exist_ok=True)
    
    print("\n[1/5] Generating test data...")
    df = generate_sales_data(num_records=300, year=2026, month=5)
    save_sales_data(df, str(data_path))
    
    print("\n[2/5] Loading and processing data...")
    df = load_sales_data(str(data_path))
    stats = get_basic_statistics(df)
    print(f"  Total Sales: ¥{stats['总销售额']:,.2f}")
    print(f"  Total Orders: {stats['订单总数']} records")
    print(f"  Average Order Value: ¥{stats['客单价']:,.2f}")
    
    print("\n[3/5] Calculating aggregated data...")
    daily_sales = aggregate_daily_sales(df)
    category_sales = aggregate_category_sales(df)
    top_categories = get_top_categories_with_other(category_sales, top_n=4)
    
    print("\n[4/5] Generating visualization charts...")
    daily_fig = create_daily_sales_chart(daily_sales)
    category_fig = create_category_pie_chart(top_categories)
    
    daily_img = get_chart_as_image(daily_fig)
    category_img = get_chart_as_image(category_fig)
    
    print("\n[5/5] Generating PDF analysis report...")
    create_pdf_report(str(pdf_path), daily_img, category_img, stats)
    
    print("\n" + "=" * 60)
    print("Analysis completed successfully!")
    print(f"Data file: {data_path.absolute()}")
    print(f"Report file: {pdf_path.absolute()}")
    print("=" * 60)

if __name__ == "__main__":
    main()
