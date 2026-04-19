from __future__ import annotations

import io
from pathlib import Path
from datetime import datetime
from typing import Dict

import polars as pl
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import plotly.graph_objects as go

from .analyzer import SalesAnalyzer
from .visualizer import SalesVisualizer


class PDFReportGenerator:
    def __init__(self, output_path: str | Path):
        self.output_path = Path(output_path)
        self._register_fonts()
        self.styles = self._create_styles()

    def _register_fonts(self):
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]

        self.chinese_font = None
        for font_path in font_paths:
            if Path(font_path).exists():
                try:
                    pdfmetrics.registerFont(TTFont("ChineseFont", font_path))
                    self.chinese_font = "ChineseFont"
                    break
                except Exception:
                    continue

        if not self.chinese_font:
            self.chinese_font = "Helvetica"

    def _create_styles(self):
        styles = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(
                name="ChineseTitle",
                fontName=self.chinese_font,
                fontSize=24,
                leading=30,
                alignment=1,
                spaceAfter=20,
            )
        )

        styles.add(
            ParagraphStyle(
                name="ChineseHeading",
                fontName=self.chinese_font,
                fontSize=16,
                leading=20,
                spaceBefore=15,
                spaceAfter=10,
            )
        )

        styles.add(
            ParagraphStyle(
                name="ChineseBody",
                fontName=self.chinese_font,
                fontSize=11,
                leading=16,
                spaceBefore=6,
                spaceAfter=6,
            )
        )

        styles.add(
            ParagraphStyle(
                name="ChineseSmall",
                fontName=self.chinese_font,
                fontSize=9,
                leading=12,
                spaceBefore=4,
                spaceAfter=4,
            )
        )

        return styles

    def _fig_to_image(self, fig: go.Figure, width: int = 700, height: int = 400) -> Image:
        img_bytes = fig.to_image(format="png", width=width, height=height, scale=1.5)
        return Image(io.BytesIO(img_bytes), width=width * 0.8, height=height * 0.8)

    def _create_summary_table(self, stats: Dict) -> Table:
        data = [
            ["指标", "数值"],
            ["总销售额", f"¥{stats['总销售额']:,.2f}"],
            ["总订单数", f"{stats['总订单数']:,}"],
            ["总用户数", f"{stats['总用户数']:,}"],
            ["平均客单价", f"¥{stats['平均客单价']:,.2f}"],
            ["总销售数量", f"{stats['总销售数量']:,}"],
        ]

        table = Table(data, colWidths=[6 * cm, 6 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f77b4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, -1), self.chinese_font),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("FONTSIZE", (0, 1), (-1, -1), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("TOPPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f0f0f0")),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#cccccc")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f8f8")]),
                ]
            )
        )
        return table

    def _create_category_table(self, category_sales: pl.DataFrame) -> Table:
        data = [["商品品类", "销售总额", "订单数", "销售数量", "占比"]]

        total = category_sales["品类销售总额"].sum()

        for row in category_sales.iter_rows(named=True):
            pct = (row["品类销售总额"] / total) * 100
            data.append([
                row["商品品类"],
                f"¥{row['品类销售总额']:,.2f}",
                f"{row['订单数']:,}",
                f"{row['销售数量']:,}",
                f"{pct:.1f}%",
            ])

        table = Table(data, colWidths=[3 * cm, 3.5 * cm, 2.5 * cm, 2.5 * cm, 2 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2ca02c")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, -1), self.chinese_font),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("TOPPADDING", (0, 0), (-1, 0), 10),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#cccccc")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f8f8")]),
                ]
            )
        )
        return table

    def generate_report(
        self,
        analyzer: SalesAnalyzer,
        visualizer: SalesVisualizer,
        report_title: str = "电商销售数据分析报告",
    ):
        stats = analyzer.get_summary_stats()
        daily_sales = analyzer.get_daily_sales()
        category_sales, total_sales = analyzer.get_top4_category_sales()

        bar_fig, pie_fig = visualizer.create_combined_figure(
            daily_sales, category_sales, total_sales
        )

        doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        story = []

        story.append(Paragraph(report_title, self.styles["ChineseTitle"]))
        story.append(
            Paragraph(
                f"报告生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
                self.styles["ChineseSmall"],
            )
        )
        story.append(Spacer(1, 0.5 * cm))

        story.append(Paragraph("一、数据概览", self.styles["ChineseHeading"]))
        story.append(
            Paragraph(
                f"本报告基于2026年5月的电商销售数据进行分析，共包含{stats['总订单数']}笔订单，"
                f"涉及{stats['总用户数']}位用户。以下为核心业务指标汇总：",
                self.styles["ChineseBody"],
            )
        )
        story.append(Spacer(1, 0.3 * cm))
        story.append(self._create_summary_table(stats))
        story.append(Spacer(1, 0.5 * cm))

        story.append(
            Paragraph(
                "从整体数据来看，本月销售表现良好。平均客单价反映了用户的购买力水平，"
                "总销售数量体现了商品的流通速度。这些指标为后续的销售策略制定提供了重要参考。",
                self.styles["ChineseBody"],
            )
        )

        story.append(PageBreak())

        story.append(Paragraph("二、每日销售趋势分析", self.styles["ChineseHeading"]))
        story.append(
            Paragraph(
                "下图展示了2026年5月每日销售总额的变化趋势。通过柱状图可以直观地观察到：",
                self.styles["ChineseBody"],
            )
        )
        story.append(Spacer(1, 0.3 * cm))

        max_daily = daily_sales.sort("日销售总额", descending=True).head(1)
        max_date = max_daily["日期"][0]
        max_sales = max_daily["日销售总额"][0]

        min_daily = daily_sales.sort("日销售总额").head(1)
        min_date = min_daily["日期"][0]
        min_sales = min_daily["日销售总额"][0]

        story.append(
            Paragraph(
                f"• 销售高峰日：{max_date}，销售额达¥{max_sales:,.2f}",
                self.styles["ChineseBody"],
            )
        )
        story.append(
            Paragraph(
                f"• 销售低谷日：{min_date}，销售额为¥{min_sales:,.2f}",
                self.styles["ChineseBody"],
            )
        )
        story.append(
            Paragraph(
                f"• 日均销售额：¥{stats['总销售额'] / len(daily_sales):,.2f}",
                self.styles["ChineseBody"],
            )
        )
        story.append(Spacer(1, 0.5 * cm))

        story.append(self._fig_to_image(bar_fig, width=500, height=300))
        story.append(Spacer(1, 0.3 * cm))

        story.append(
            Paragraph(
                "从趋势图可以看出，销售数据呈现出一定的波动性。周末和促销活动期间往往会出现销售高峰，"
                "而工作日中旬可能出现相对平稳的销售态势。建议根据销售高峰时段合理调配库存和人力资源。",
                self.styles["ChineseBody"],
            )
        )

        story.append(PageBreak())

        story.append(Paragraph("三、商品品类销售占比分析", self.styles["ChineseHeading"]))
        story.append(
            Paragraph(
                "为深入了解各商品品类的销售贡献，我们对销售数据进行了品类维度的聚合分析。"
                '以下饼图展示了销售额排名前4的品类及其占比情况，其余品类合并为"其他"类别：',
                self.styles["ChineseBody"],
            )
        )
        story.append(Spacer(1, 0.5 * cm))

        story.append(self._fig_to_image(pie_fig, width=450, height=300))
        story.append(Spacer(1, 0.5 * cm))

        story.append(Paragraph("品类销售明细：", self.styles["ChineseBody"]))
        story.append(Spacer(1, 0.3 * cm))
        story.append(self._create_category_table(category_sales))
        story.append(Spacer(1, 0.5 * cm))

        top_category = category_sales.head(1)
        top_cat_name = top_category["商品品类"][0]
        top_cat_sales = top_category["品类销售总额"][0]
        top_cat_pct = (top_cat_sales / total_sales) * 100

        story.append(
            Paragraph(
                f'分析结果显示，"{top_cat_name}"品类以¥{top_cat_sales:,.2f}的销售额领跑，'
                f"占总销售额的{top_cat_pct:.1f}%。这一数据反映了消费者对该品类商品的强劲需求。"
                "建议针对热销品类加大营销投入和库存保障，同时挖掘潜力品类的增长空间。",
                self.styles["ChineseBody"],
            )
        )

        story.append(PageBreak())

        story.append(Paragraph("四、总结与建议", self.styles["ChineseHeading"]))
        story.append(
            Paragraph(
                f"综合以上分析，2026年5月的电商销售数据呈现以下特点：",
                self.styles["ChineseBody"],
            )
        )
        story.append(Spacer(1, 0.3 * cm))

        story.append(
            Paragraph(
                f"1. 整体销售表现：本月实现总销售额¥{stats['总销售额']:,.2f}，"
                f"平均客单价¥{stats['平均客单价']:,.2f}，显示出良好的销售势头。",
                self.styles["ChineseBody"],
            )
        )
        story.append(
            Paragraph(
                f"2. 品类结构：{top_cat_name}是销售主力，建议持续优化该品类的商品结构和营销策略。",
                self.styles["ChineseBody"],
            )
        )
        story.append(
            Paragraph(
                "3. 时间分布：销售数据存在明显的日间波动，建议在销售高峰期加强运营支持。",
                self.styles["ChineseBody"],
            )
        )
        story.append(Spacer(1, 0.5 * cm))

        story.append(
            Paragraph(
                "基于以上分析，建议采取以下措施：优化热销品类的库存管理；"
                "针对销售低谷期策划促销活动；加强用户运营，提升复购率和客单价。"
                "持续关注销售数据变化，及时调整经营策略，以实现销售业绩的稳步增长。",
                self.styles["ChineseBody"],
            )
        )

        doc.build(story)
        print(f"PDF report generated: {self.output_path}")
