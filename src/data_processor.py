import polars as pl
from typing import Tuple, List, Dict
from datetime import datetime


class SalesDataProcessor:
    """销售数据处理器"""
    
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.df = None
        self._load_data()
    
    def _load_data(self):
        """加载CSV数据"""
        self.df = pl.read_csv(self.csv_path, encoding="utf-8")
        # 转换下单时间为日期类型
        self.df = self.df.with_columns([
            pl.col("下单时间").str.to_datetime("%Y-%m-%d %H:%M").alias("下单时间"),
            pl.col("下单时间").str.to_datetime("%Y-%m-%d %H:%M").dt.date().alias("日期")
        ])
    
    def get_daily_sales(self) -> pl.DataFrame:
        """按天统计销售总金额"""
        daily_sales = self.df.group_by("日期").agg([
            pl.col("总价").sum().alias("日销售额"),
            pl.col("订单ID").count().alias("订单数")
        ]).sort("日期")
        return daily_sales
    
    def get_category_sales(self, top_n: int = 4) -> Tuple[pl.DataFrame, pl.DataFrame]:
        """
        按品类统计销售占比
        返回: (前N名品类数据, 其他品类汇总数据)
        """
        category_sales = self.df.group_by("商品品类").agg([
            pl.col("总价").sum().alias("品类销售额"),
            pl.col("订单ID").count().alias("订单数")
        ]).sort("品类销售额", descending=True)
        
        # 获取前N名
        top_categories = category_sales.head(top_n)
        
        # 计算其他品类
        if len(category_sales) > top_n:
            others = category_sales.tail(len(category_sales) - top_n)
            others_sum = others.select([
                pl.lit("其他").alias("商品品类"),
                pl.col("品类销售额").sum().alias("品类销售额"),
                pl.col("订单数").sum().alias("订单数")
            ])
        else:
            others_sum = pl.DataFrame({
                "商品品类": [],
                "品类销售额": [],
                "订单数": []
            })
        
        return top_categories, others_sum
    
    def get_summary_stats(self) -> Dict:
        """获取汇总统计信息"""
        total_sales = self.df["总价"].sum()
        total_orders = self.df.shape[0]
        unique_users = self.df["用户ID"].n_unique()
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        
        # 找出最佳销售日
        daily_sales = self.get_daily_sales()
        best_day = daily_sales.sort("日销售额", descending=True).head(1)
        
        # 找出最佳品类
        category_sales = self.df.group_by("商品品类").agg([
            pl.col("总价").sum().alias("品类销售额")
        ]).sort("品类销售额", descending=True).head(1)
        
        return {
            "总销售额": round(total_sales, 2),
            "总订单数": total_orders,
            "独立用户数": unique_users,
            "平均客单价": round(avg_order_value, 2),
            "最佳销售日": best_day["日期"][0].strftime("%Y-%m-%d") if len(best_day) > 0 else "N/A",
            "最佳销售日金额": round(best_day["日销售额"][0], 2) if len(best_day) > 0 else 0,
            "最佳品类": category_sales["商品品类"][0] if len(category_sales) > 0 else "N/A",
            "最佳品类销售额": round(category_sales["品类销售额"][0], 2) if len(category_sales) > 0 else 0
        }


if __name__ == "__main__":
    # 测试代码
    processor = SalesDataProcessor("data/sales_data_2026_05.csv")
    print("日销售统计:")
    print(processor.get_daily_sales())
    print("\n品类销售统计:")
    top, others = processor.get_category_sales()
    print(top)
    print(others)
    print("\n汇总统计:")
    print(processor.get_summary_stats())
