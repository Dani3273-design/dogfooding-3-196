import polars as pl
from pathlib import Path

def load_sales_data(file_path: str) -> pl.DataFrame:
    df = pl.read_csv(file_path, try_parse_dates=True)
    return df

def aggregate_daily_sales(df: pl.DataFrame) -> pl.DataFrame:
    daily_sales = df.with_columns(
        pl.col("下单时间").dt.date().alias("日期")
    ).group_by("日期").agg(
        pl.col("总价").sum().alias("销售总金额")
    ).sort("日期")
    return daily_sales

def aggregate_category_sales(df: pl.DataFrame) -> pl.DataFrame:
    category_sales = df.group_by("商品品类").agg(
        pl.col("总价").sum().alias("销售总金额")
    ).sort("销售总金额", descending=True)
    return category_sales

def get_top_categories_with_other(category_sales: pl.DataFrame, top_n: int = 4) -> pl.DataFrame:
    top_categories = category_sales.head(top_n)
    other_amount = category_sales[top_n:]["销售总金额"].sum()
    other_row = pl.DataFrame({
        "商品品类": ["其他"],
        "销售总金额": [other_amount]
    })
    result = pl.concat([top_categories, other_row])
    return result

def get_basic_statistics(df: pl.DataFrame) -> dict:
    total_sales = df["总价"].sum()
    total_orders = df.height
    avg_order_value = total_sales / total_orders
    unique_users = df["用户ID"].n_unique()
    peak_day_df = aggregate_daily_sales(df).sort("销售总金额", descending=True).head(1)
    peak_day = peak_day_df["日期"][0]
    peak_day_sales = peak_day_df["销售总金额"][0]
    
    top_category_df = aggregate_category_sales(df).head(1)
    top_category = top_category_df["商品品类"][0]
    top_category_sales = top_category_df["销售总金额"][0]
    
    return {
        "总销售额": round(total_sales, 2),
        "订单总数": total_orders,
        "客单价": round(avg_order_value, 2),
        "独立用户数": unique_users,
        "销售峰值日": peak_day,
        "峰值日销售额": round(peak_day_sales, 2),
        "最畅销品类": top_category,
        "最畅销品类销售额": round(top_category_sales, 2)
    }
