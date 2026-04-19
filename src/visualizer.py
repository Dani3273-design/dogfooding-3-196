from __future__ import annotations

import polars as pl
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Tuple


class SalesVisualizer:
    def __init__(self):
        self.colors = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
        ]

    def create_daily_bar_chart(self, daily_sales: pl.DataFrame) -> go.Figure:
        dates = daily_sales["日期"].to_list()
        sales = daily_sales["日销售总额"].to_list()
        orders = daily_sales["订单数"].to_list()

        date_labels = [str(d) for d in dates]

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Bar(
                x=date_labels,
                y=sales,
                name="Daily Revenue",
                marker_color="#1f77b4",
                text=[f"{s:,.0f}" for s in sales],
                textposition="outside",
                textfont={"size": 9},
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=date_labels,
                y=orders,
                mode="lines+markers",
                name="Orders",
                line=dict(color="#ff7f0e", width=2),
                marker=dict(size=6),
            ),
            secondary_y=True,
        )

        fig.update_layout(
            title={
                "text": "Daily Sales Revenue Statistics",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18, "family": "SimHei"},
            },
            xaxis_title="Date",
            yaxis_title="Revenue (CNY)",
            yaxis2_title="Orders",
            template="plotly_white",
            height=500,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=80, b=80, l=60, r=60),
        )

        fig.update_xaxes(tickangle=45, tickfont={"size": 9})
        fig.update_yaxes(tickformat=",.0f", secondary_y=False)
        fig.update_yaxes(tickformat="d", secondary_y=True)

        return fig

    def create_category_pie_chart(
        self, category_sales: pl.DataFrame, total_sales: float
    ) -> go.Figure:
        categories = category_sales["商品品类"].to_list()
        sales = category_sales["品类销售总额"].to_list()

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=categories,
                    values=sales,
                    hole=0.3,
                    textinfo="label+percent",
                    textfont={"size": 12, "family": "SimHei"},
                    marker=dict(colors=self.colors[: len(categories)]),
                    hovertemplate="<b>%{label}</b><br>Revenue: %{value:,.0f} CNY<br>Percentage: %{percent}<extra></extra>",
                )
            ]
        )

        fig.update_layout(
            title={
                "text": "Category Sales Distribution<br><sub>(Top 4 Categories + Others)</sub>",
                "x": 0.5,
                "xanchor": "center",
                "font": {"size": 18, "family": "SimHei"},
            },
            template="plotly_white",
            height=500,
            showlegend=True,
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5
            ),
            margin=dict(t=80, b=100, l=60, r=60),
        )

        return fig

    def create_combined_figure(
        self,
        daily_sales: pl.DataFrame,
        category_sales: pl.DataFrame,
        total_sales: float,
    ) -> Tuple[go.Figure, go.Figure]:
        bar_fig = self.create_daily_bar_chart(daily_sales)
        pie_fig = self.create_category_pie_chart(category_sales, total_sales)
        return bar_fig, pie_fig
