import random
import csv
from datetime import datetime, timedelta
from typing import List, Dict


class SalesDataGenerator:
    """销售数据生成器"""
    
    CATEGORIES = [
        "手机数码", "家用电器", "服装鞋包", "食品生鲜",
        "美妆个护", "家居家装", "母婴用品", "运动户外"
    ]
    
    # 各品类价格范围
    PRICE_RANGES = {
        "手机数码": (1000, 8000),
        "家用电器": (500, 5000),
        "服装鞋包": (100, 1500),
        "食品生鲜": (20, 300),
        "美妆个护": (50, 800),
        "家居家装": (200, 3000),
        "母婴用品": (100, 2000),
        "运动户外": (150, 2500)
    }
    
    # 各品类购买数量范围
    QUANTITY_RANGES = {
        "手机数码": (1, 2),
        "家用电器": (1, 3),
        "服装鞋包": (1, 5),
        "食品生鲜": (1, 10),
        "美妆个护": (1, 5),
        "家居家装": (1, 4),
        "母婴用品": (1, 6),
        "运动户外": (1, 3)
    }
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
    
    def _generate_order_time(self, year: int, month: int) -> datetime:
        """生成订单时间，考虑黄金时段规律"""
        # 生成该月的随机一天
        days_in_month = 31 if month in [1, 3, 5, 7, 8, 10, 12] else 30
        if month == 2:
            days_in_month = 28
        
        day = random.randint(1, days_in_month)
        
        # 黄金时段权重：10-12点、14-16点、20-22点订单较多
        hour_weights = []
        for h in range(24):
            if 10 <= h <= 12 or 14 <= h <= 16 or 20 <= h <= 22:
                hour_weights.append(3)
            elif 9 <= h <= 17:
                hour_weights.append(2)
            else:
                hour_weights.append(1)
        
        hour = random.choices(range(24), weights=hour_weights)[0]
        minute = random.randint(0, 59)
        
        return datetime(year, month, day, hour, minute)
    
    def _generate_user_id(self) -> str:
        """生成用户ID"""
        return f"U{random.randint(10000, 99999):05d}"
    
    def _generate_order_id(self, index: int) -> str:
        """生成订单ID"""
        return f"ORD{datetime.now().strftime('%Y%m%d')}{index:06d}"
    
    def generate_record(self, index: int, year: int, month: int) -> Dict:
        """生成单条销售记录"""
        category = random.choice(self.CATEGORIES)
        price_range = self.PRICE_RANGES[category]
        quantity_range = self.QUANTITY_RANGES[category]
        
        unit_price = round(random.uniform(price_range[0], price_range[1]), 2)
        quantity = random.randint(quantity_range[0], quantity_range[1])
        total_price = round(unit_price * quantity, 2)
        
        return {
            "订单ID": self._generate_order_id(index),
            "用户ID": self._generate_user_id(),
            "下单时间": self._generate_order_time(year, month).strftime("%Y-%m-%d %H:%M"),
            "商品品类": category,
            "单价": unit_price,
            "数量": quantity,
            "总价": total_price
        }
    
    def generate_data(self, count: int, year: int, month: int) -> List[Dict]:
        """生成指定数量的销售数据"""
        return [self.generate_record(i, year, month) for i in range(count)]
    
    def save_to_csv(self, data: List[Dict], filepath: str):
        """保存数据到CSV文件"""
        if not data:
            return
        
        fieldnames = ["订单ID", "用户ID", "下单时间", "商品品类", "单价", "数量", "总价"]
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        print(f"数据已保存到: {filepath}")


def generate_test_data(output_path: str = "data/sales_data_2026_05.csv", 
                       count: int = 300,
                       year: int = 2026,
                       month: int = 5):
    """生成测试数据入口函数"""
    generator = SalesDataGenerator(seed=42)
    data = generator.generate_data(count, year, month)
    generator.save_to_csv(data, output_path)
    return output_path


if __name__ == "__main__":
    generate_test_data()
