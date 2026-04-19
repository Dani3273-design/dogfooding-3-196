import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import polars as pl
from pathlib import Path
import io

COLORS = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]

def create_daily_sales_chart(daily_sales: pl.DataFrame, title: str = "Daily Sales Trend - May 2026") -> go.Figure:
    dates = daily_sales["日期"].to_list()
    sales = daily_sales["销售总金额"].to_list()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dates,
        y=sales,
        marker_color="#45B7D1",
        marker_line_color="#2980b9",
        marker_line_width=1,
        opacity=0.8,
        name="销售额",
        text=[f"¥{v:,.2f}" for v in sales],
        textposition="outside",
    ))
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=sales,
        mode="lines+markers",
        line=dict(color="#FF6B6B", width=2),
        marker=dict(size=6),
        name="趋势线"
    ))
    
    fig.update_layout(
        title={
            "text": title,
            "font": {"size": 20, "color": "#333"},
            "x": 0.5,
            "y": 0.95
        },
        xaxis_title="日期",
        yaxis_title="销售金额 (元)",
        hovermode="x unified",
        plot_bgcolor="white",
        height=500,
        margin=dict(l=60, r=60, t=80, b=60),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(
        tickangle=45,
        gridcolor="#f0f0f0",
        showgrid=True
    )
    
    fig.update_yaxes(
        gridcolor="#f0f0f0",
        tickformat=",",
        hoverformat=",.2f"
    )
    
    return fig

def create_category_pie_chart(category_sales: pl.DataFrame, title: str = "Sales Distribution by Category") -> go.Figure:
    categories = category_sales["商品品类"].to_list()
    sales = category_sales["销售总金额"].to_list()
    total = sum(sales)
    percentages = [s / total * 100 for s in sales]
    
    text_labels = [
        f"{cat}<br>¥{sale:,.2f}<br>({pct:.1f}%)"
        for cat, sale, pct in zip(categories, sales, percentages)
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=categories,
        values=sales,
        text=text_labels,
        textinfo="text",
        hoverinfo="label+percent+value",
        marker=dict(
            colors=COLORS[:len(categories)],
            line=dict(color="#ffffff", width=2)
        ),
        pull=[0.05, 0.05, 0.05, 0.05, 0],
        hole=0.3
    ))
    
    fig.update_layout(
        title={
            "text": title,
            "font": {"size": 20, "color": "#333"},
            "x": 0.5,
            "y": 0.95
        },
        height=550,
        margin=dict(l=40, r=40, t=80, b=40),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        )
    )
    
    return fig

def save_chart_image(fig: go.Figure, output_path: str, width: int = 1000, height: int = 600) -> None:
    fig.write_image(output_path, width=width, height=height, scale=2)

def get_chart_as_image(fig: go.Figure, width: int = 1000, height: int = 600) -> bytes:
    img_bytes = fig.to_image(format="png", width=width, height=height, scale=2)
    return img_bytes
