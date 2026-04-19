#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from src.data_generator import generate_sales_data, save_to_csv
from src.analyzer import SalesAnalyzer
from src.visualizer import SalesVisualizer
from src.report_generator import PDFReportGenerator


def main():
    parser = argparse.ArgumentParser(description="E-commerce Sales Data Analysis Program")
    parser.add_argument(
        "--generate-data",
        action="store_true",
        help="Generate test data (300 records for May 2026)",
    )
    parser.add_argument(
        "--data-file",
        type=str,
        default="data/sales_data_202605.csv",
        help="Sales data file path (default: data/sales_data_202605.csv)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output/sales_report.pdf",
        help="PDF report output path (default: output/sales_report.pdf)",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2026,
        help="Data year (default: 2026)",
    )
    parser.add_argument(
        "--month",
        type=int,
        default=5,
        help="Data month (default: 5)",
    )
    parser.add_argument(
        "--records",
        type=int,
        default=300,
        help="Number of records to generate (default: 300)",
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    output_dir = project_root / "output"

    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.generate_data:
        print(f"Generating {args.records} sales records for {args.year}-{args.month:02d}...")
        df = generate_sales_data(
            num_records=args.records, year=args.year, month=args.month
        )
        data_path = data_dir / f"sales_data_{args.year}{str(args.month).zfill(2)}.csv"
        save_to_csv(df, data_path)
        print(f"Data saved to: {data_path}")
        print(f"Total {len(df)} records generated\n")

    data_path = project_root / args.data_file
    if not data_path.exists():
        print(f"Error: Data file not found: {data_path}")
        print("Please use --generate-data flag to generate test data first")
        sys.exit(1)

    print(f"Analyzing data: {data_path}")
    analyzer = SalesAnalyzer(data_path)

    stats = analyzer.get_summary_stats()
    print("\n=== Data Overview ===")
    print(f"Total Revenue: {stats['总销售额']:,.2f} CNY")
    print(f"Total Orders: {stats['总订单数']}")
    print(f"Total Users: {stats['总用户数']}")
    print(f"Average Order Value: {stats['平均客单价']:,.2f} CNY")
    print(f"Total Quantity Sold: {stats['总销售数量']}")

    print("\nGenerating visualization charts...")
    visualizer = SalesVisualizer()

    output_path = project_root / args.output
    print(f"Generating PDF report: {output_path}")
    report_generator = PDFReportGenerator(output_path)
    report_generator.generate_report(analyzer, visualizer)

    print("\n=== Analysis Complete ===")
    print(f"PDF report saved to: {output_path}")


if __name__ == "__main__":
    main()
