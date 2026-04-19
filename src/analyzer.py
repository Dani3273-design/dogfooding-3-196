from __future__ import annotations

from pathlib import Path
from typing import Tuple
import polars as pl


class SalesAnalyzer:
    def __init__(self, data_path: str | Path):
        self.data_path = Path(data_path)
        self.df: pl.DataFrame = None
        self.load_data()

    def load_data(self) -> None:
        self.df = pl.read_csv(self.data_path)
        self.df = self.df.with_columns(
            pl.col("下单时间").str.to_datetime("%Y-%m-%d %H:%M").alias("下单时间_dt")
        )
        self.df = self.df.with_columns(
            pl.col("下单时间_dt").dt.date().alias("日期"),
            pl.col("下单时间_dt").dt.hour().alias("小时"),
        )

    def get_daily_sales(self) -> pl.DataFrame:
        daily_sales = (
            self.df.group_by("日期")
            .agg([pl.col("总价").sum().alias("日销售总额"), pl.col("订单ID").n_unique().alias("订单数")])
            .sort("日期")
        )
        return daily_sales

    def get_category_sales(self) -> pl.DataFrame:
        category_sales = (
            self.df.group_by("商品品类")
            .agg([
                pl.col("总价").sum().alias("品类销售总额"),
                pl.col("订单ID").n_unique().alias("订单数"),
                pl.col("数量").sum().alias("销售数量"),
            ])
            .sort("品类销售总额", descending=True)
        )
        return category_sales

    def get_top4_category_sales(self) -> Tuple[pl.DataFrame, float]:
        category_sales = self.get_category_sales()
        top4 = category_sales.head(4).clone()
        total_sales = float(category_sales["品类销售总额"].sum())
        top4_sales = float(top4["品类销售总额"].sum())
        other_sales = total_sales - top4_sales

        other_orders = int(category_sales[4:]["订单数"].sum()) if len(category_sales) > 4 else 0
        other_quantity = int(category_sales[4:]["销售数量"].sum()) if len(category_sales) > 4 else 0

        other_row = pl.DataFrame({
            "商品品类": ["其他"],
            "品类销售总额": [other_sales],
            "订单数": [other_orders],
            "销售数量": [other_quantity],
        })

        top4 = top4.with_columns([
            pl.col("品类销售总额").cast(pl.Float64),
            pl.col("订单数").cast(pl.Int64),
            pl.col("销售数量").cast(pl.Int64),
        ])

        result = pl.concat([top4, other_row])
        return result, total_sales

    def get_summary_stats(self) -> dict:
        total_revenue = self.df["总价"].sum()
        total_orders = self.df["订单ID"].n_unique()
        total_users = self.df["用户ID"].n_unique()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        total_quantity = self.df["数量"].sum()

        return {
            "总销售额": round(total_revenue, 2),
            "总订单数": total_orders,
            "总用户数": total_users,
            "平均客单价": round(avg_order_value, 2),
            "总销售数量": total_quantity,
        }

    def get_hourly_distribution(self) -> pl.DataFrame:
        hourly = (
            self.df.group_by("小时")
            .agg([pl.col("总价").sum().alias("销售总额"), pl.col("订单ID").n_unique().alias("订单数")])
            .sort("小时")
        )
        return hourly
