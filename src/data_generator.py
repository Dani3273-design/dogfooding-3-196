import polars as pl
import random
from datetime import datetime, timedelta
from typing import List, Dict

CATEGORIES = [
    "手机数码", "家用电器", "服装鞋包", "食品生鲜",
    "美妆个护", "家居家装", "母婴用品", "运动户外"
]

CATEGORY_PRICE_RANGES = {
    "手机数码": (2000, 8000),
    "家用电器": (500, 5000),
    "服装鞋包": (50, 800),
    "食品生鲜": (10, 300),
    "美妆个护": (50, 1000),
    "家居家装": (100, 3000),
    "母婴用品": (30, 800),
    "运动户外": (100, 2000)
}

CATEGORY_WEIGHTS = [0.18, 0.12, 0.20, 0.15, 0.12, 0.08, 0.08, 0.07]

def generate_order_time(year: int, month: int) -> datetime:
    day = random.randint(1, 31)
    hour_weights = [1] * 24
    for h in range(10, 13):
        hour_weights[h] = 5
    for h in range(14, 17):
        hour_weights[h] = 4
    for h in range(19, 23):
        hour_weights[h] = 6
    for h in range(0, 8):
        hour_weights[h] = 0.5
    
    hours = list(range(24))
    hour = random.choices(hours, weights=hour_weights, k=1)[0]
    minute = random.randint(0, 59)
    
    try:
        return datetime(year, month, day, hour, minute)
    except ValueError:
        return generate_order_time(year, month)

def generate_sales_data(num_records: int = 300, year: int = 2026, month: int = 5) -> pl.DataFrame:
    records: List[Dict] = []
    
    for order_id in range(1, num_records + 1):
        user_id = random.randint(10001, 10500)
        order_time = generate_order_time(year, month)
        category = random.choices(CATEGORIES, weights=CATEGORY_WEIGHTS, k=1)[0]
        price_min, price_max = CATEGORY_PRICE_RANGES[category]
        unit_price = round(random.uniform(price_min, price_max), 2)
        quantity = random.choices([1, 2, 3, 4, 5], weights=[0.6, 0.25, 0.1, 0.03, 0.02], k=1)[0]
        total_price = round(unit_price * quantity, 2)
        
        records.append({
            "订单ID": f"ORD{order_id:06d}",
            "用户ID": f"USER{user_id:05d}",
            "下单时间": order_time,
            "商品品类": category,
            "单价": unit_price,
            "数量": quantity,
            "总价": total_price
        })
    
    df = pl.DataFrame(records)
    df = df.sort("下单时间")
    return df

def save_sales_data(df: pl.DataFrame, output_path: str) -> None:
    df.write_csv(output_path)
    print(f"Data saved to: {output_path}")
    print(f"Generated {df.height} sales records")

if __name__ == "__main__":
    df = generate_sales_data(300, 2026, 5)
    save_sales_data(df, "../data/sales_data_202605.csv")
