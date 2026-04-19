from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import polars as pl

CATEGORIES = [
    "手机数码",
    "家用电器",
    "服装鞋包",
    "食品生鲜",
    "美妆个护",
    "家居家装",
    "母婴用品",
    "运动户外",
]

CATEGORY_PRICE_RANGE = {
    "手机数码": (500, 8000),
    "家用电器": (200, 5000),
    "服装鞋包": (50, 2000),
    "食品生鲜": (10, 500),
    "美妆个护": (30, 1000),
    "家居家装": (100, 3000),
    "母婴用品": (20, 800),
    "运动户外": (50, 1500),
}

GOLDEN_HOURS = list(range(19, 23)) + list(range(10, 14))
PEAK_HOURS = list(range(19, 22))
NORMAL_HOURS = list(range(8, 10)) + list(range(14, 19)) + list(range(23, 24))
LOW_HOURS = list(range(0, 8))


def generate_order_time(year: int, month: int) -> datetime:
    days_in_month = 31
    day = random.randint(1, days_in_month)

    hour_weights = []
    available_hours = list(range(24))
    for h in available_hours:
        if h in PEAK_HOURS:
            hour_weights.extend([h] * 5)
        elif h in GOLDEN_HOURS:
            hour_weights.extend([h] * 3)
        elif h in NORMAL_HOURS:
            hour_weights.extend([h] * 2)
        else:
            hour_weights.extend([h] * 1)

    hour = random.choice(hour_weights)
    minute = random.randint(0, 59)

    return datetime(year, month, day, hour, minute)


def generate_single_order(order_id: str, user_id: str, year: int, month: int) -> dict:
    category = random.choice(CATEGORIES)
    price_range = CATEGORY_PRICE_RANGE[category]
    unit_price = round(random.uniform(price_range[0], price_range[1]), 2)

    if category in ["食品生鲜", "母婴用品", "美妆个护"]:
        quantity = random.choices([1, 2, 3, 4, 5], weights=[30, 30, 20, 15, 5])[0]
    elif category in ["手机数码", "家用电器"]:
        quantity = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
    else:
        quantity = random.choices([1, 2, 3, 4], weights=[40, 30, 20, 10])[0]

    total_price = round(unit_price * quantity, 2)
    order_time = generate_order_time(year, month)

    return {
        "订单ID": order_id,
        "用户ID": user_id,
        "下单时间": order_time.strftime("%Y-%m-%d %H:%M"),
        "商品品类": category,
        "单价": unit_price,
        "数量": quantity,
        "总价": total_price,
    }


def generate_sales_data(
    num_records: int = 300, year: int = 2026, month: int = 5
) -> pl.DataFrame:
    orders = []
    user_pool = [f"U{str(i).zfill(6)}" for i in range(1, 151)]

    for _ in range(num_records):
        order_id = f"ORD{uuid.uuid4().hex[:10].upper()}"
        user_id = random.choice(user_pool)
        order = generate_single_order(order_id, user_id, year, month)
        orders.append(order)

    df = pl.DataFrame(orders)
    df = df.sort("下单时间")
    return df


def save_to_csv(df: pl.DataFrame, output_path: str | Path) -> None:
    df.write_csv(output_path)


def main():
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)

    df = generate_sales_data(num_records=300, year=2026, month=5)
    output_path = output_dir / "sales_data_202605.csv"
    save_to_csv(df, output_path)

    print(f"Generated {len(df)} sales records")
    print(f"Data saved to: {output_path}")
    print(f"\nData preview:")
    print(df.head(10))


if __name__ == "__main__":
    main()
