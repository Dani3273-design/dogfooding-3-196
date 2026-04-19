import plotly.graph_objects as go
import polars as pl
from typing import Tuple


class SalesVisualizer:
    """销售数据可视化器"""
    
    def __init__(self, theme: str = "plotly_white"):
        self.theme = theme
        self.colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
            "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"
        ]
    
    def create_daily_sales_chart(self, daily_data: pl.DataFrame) -> go.Figure:
        """创建日销售额柱状图"""
        dates = daily_data["日期"].to_list()
        sales = daily_data["日销售额"].to_list()
        
        fig = go.Figure(data=[
            go.Bar(
                x=[d.strftime("%m-%d") for d in dates],
                y=sales,
                marker_color=self.colors[0],
                text=[f"¥{s:,.0f}" for s in sales],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>销售额: ¥%{y:,.2f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title={
                'text': '2026年5月每日销售额统计',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': '#2C3E50'}
            },
            xaxis_title='日期',
            yaxis_title='销售额 (元)',
            template=self.theme,
            height=600,
            xaxis_tickangle=-45,
            yaxis_tickformat=',.0f',
            showlegend=False,
            margin=dict(l=80, r=80, t=100, b=100)
        )
        
        # 添加网格线
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        
        return fig
    
    def create_category_pie_chart(self, top_data: pl.DataFrame, others_data: pl.DataFrame) -> go.Figure:
        """创建品类销售占比饼图"""
        categories = top_data["商品品类"].to_list()
        sales = top_data["品类销售额"].to_list()
        
        # 如果有其他品类，添加进去
        if len(others_data) > 0 and others_data["品类销售额"][0] > 0:
            categories.append("其他")
            sales.append(others_data["品类销售额"][0])
        
        # 计算百分比
        total = sum(sales)
        percentages = [s / total * 100 for s in sales]
        
        fig = go.Figure(data=[
            go.Pie(
                labels=categories,
                values=sales,
                hole=0.4,
                marker_colors=self.colors[:len(categories)],
                textinfo='label+percent',
                textposition='outside',
                textfont_size=12,
                hovertemplate='<b>%{label}</b><br>销售额: ¥%{value:,.2f}<br>占比: %{percent}<extra></extra>',
                customdata=[[f"¥{s:,.2f}"] for s in sales],
                texttemplate='%{label}<br>%{percent:.1%}'
            )
        ])
        
        fig.update_layout(
            title={
                'text': '商品品类销售占比分析<br><sub>（显示销售额前4名品类，其余归为其他）</sub>',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 22, 'color': '#2C3E50'}
            },
            template=self.theme,
            height=600,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=80, r=80, t=120, b=100),
            annotations=[
                dict(
                    text=f'总销售额<br>¥{total:,.0f}',
                    x=0.5, y=0.5,
                    font_size=16,
                    showarrow=False
                )
            ]
        )
        
        return fig


if __name__ == "__main__":
    # 测试代码
    from data_processor import SalesDataProcessor
    
    processor = SalesDataProcessor("data/sales_data_2026_05.csv")
    visualizer = SalesVisualizer()
    
    daily_data = processor.get_daily_sales()
    top_data, others_data = processor.get_category_sales(top_n=4)
    
    fig1 = visualizer.create_daily_sales_chart(daily_data)
    fig1.write_html("output/test_daily_chart.html")
    
    fig2 = visualizer.create_category_pie_chart(top_data, others_data)
    fig2.write_html("output/test_pie_chart.html")
    
    print("测试图表已生成到 output/ 目录")
