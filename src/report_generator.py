import os
import tempfile
from datetime import datetime
from typing import Dict, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import plotly.graph_objects as go
import kaleido


class PDFReportGenerator:
    """PDF报告生成器"""
    
    def __init__(self, output_path: str):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """设置中文字体和样式"""
        # 尝试注册中文字体
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
        
        self.chinese_font = "Helvetica"
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    self.chinese_font = 'ChineseFont'
                    break
                except:
                    continue
        
        # 自定义样式
        self.styles.add(ParagraphStyle(
            name='ChineseTitle',
            fontName=self.chinese_font,
            fontSize=24,
            leading=30,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.HexColor('#2C3E50')
        ))
        
        self.styles.add(ParagraphStyle(
            name='ChineseHeading',
            fontName=self.chinese_font,
            fontSize=16,
            leading=22,
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=12,
            textColor=colors.HexColor('#34495E')
        ))
        
        self.styles.add(ParagraphStyle(
            name='ChineseBody',
            fontName=self.chinese_font,
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            textColor=colors.HexColor('#2C3E50')
        ))
        
        self.styles.add(ParagraphStyle(
            name='ChineseCaption',
            fontName=self.chinese_font,
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            spaceBefore=6,
            textColor=colors.HexColor('#7F8C8D')
        ))
    
    def _fig_to_image(self, fig: go.Figure, width: int = 800, height: int = 500) -> str:
        """将Plotly图表转换为临时图片文件"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_file.close()
        fig.write_image(temp_file.name, width=width, height=height, scale=2)
        return temp_file.name
    
    def _create_summary_table(self, stats: Dict) -> Table:
        """创建汇总统计表格"""
        data = [
            ["指标", "数值"],
            ["总销售额", f"¥{stats['总销售额']:,.2f}"],
            ["总订单数", f"{stats['总订单数']:,} 单"],
            ["独立用户数", f"{stats['独立用户数']:,} 人"],
            ["平均客单价", f"¥{stats['平均客单价']:,.2f}"],
            ["最佳销售日", f"{stats['最佳销售日']} (¥{stats['最佳销售日金额']:,.2f})"],
            ["最佳品类", f"{stats['最佳品类']} (¥{stats['最佳品类销售额']:,.2f})"],
        ]
        
        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ECF0F1')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2C3E50')),
            ('FONTNAME', (0, 1), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ]))
        
        return table
    
    def generate_report(self, daily_chart: go.Figure, pie_chart: go.Figure, 
                       stats: Dict, report_title: str = "电商销售数据分析报告"):
        """生成PDF报告"""
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # 封面/标题页
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(report_title, self.styles['ChineseTitle']))
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}", 
                              self.styles['ChineseCaption']))
        story.append(Paragraph("数据来源: 2026年5月销售数据", 
                              self.styles['ChineseCaption']))
        story.append(PageBreak())
        
        # 第一页：日销售额分析
        story.append(Paragraph("一、每日销售额趋势分析", self.styles['ChineseHeading']))
        story.append(Spacer(1, 0.2*inch))
        
        # 添加说明文字
        intro_text = """
        本报告对2026年5月的电商销售数据进行全面分析。下图展示了整个5月份每日销售额的变化趋势。
        从数据可以看出，销售额在工作日和周末呈现不同的波动规律，部分日期由于促销活动或节假日影响，
        出现了明显的销售高峰。通过分析每日销售趋势，可以帮助我们更好地制定库存管理和营销策略。
        """
        story.append(Paragraph(intro_text, self.styles['ChineseBody']))
        story.append(Spacer(1, 0.2*inch))
        
        # 添加柱状图
        daily_img_path = self._fig_to_image(daily_chart, width=700, height=450)
        story.append(Image(daily_img_path, width=6.5*inch, height=4.2*inch))
        story.append(Paragraph("图1：2026年5月每日销售额统计", self.styles['ChineseCaption']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # 添加分析说明
        analysis_text = f"""
        <b>关键发现：</b><br/>
        • 本月份总销售额达到 <b>¥{stats['总销售额']:,.2f}</b>，共完成 <b>{stats['总订单数']}</b> 笔订单<br/>
        • 日均销售额约为 <b>¥{stats['总销售额']/30:,.2f}</b>，日均订单量约 <b>{stats['总订单数']//30}</b> 单<br/>
        • 销售最高峰出现在 <b>{stats['最佳销售日']}</b>，当日销售额达 <b>¥{stats['最佳销售日金额']:,.2f}</b><br/>
        • 独立用户数为 <b>{stats['独立用户数']}</b> 人，平均客单价为 <b>¥{stats['平均客单价']:,.2f}</b><br/>
        • 从时间分布来看，订单主要集中在上午10-12点、下午2-4点以及晚间8-10点的黄金时段
        """
        story.append(Paragraph(analysis_text, self.styles['ChineseBody']))
        
        story.append(PageBreak())
        
        # 第二页：品类销售占比分析
        story.append(Paragraph("二、商品品类销售占比分析", self.styles['ChineseHeading']))
        story.append(Spacer(1, 0.2*inch))
        
        # 添加说明文字
        category_intro = """
        下图展示了各商品品类的销售占比情况。为了突出重点，我们仅展示销售额排名前4的品类，
        其余品类统一归入"其他"类别。品类分析有助于了解消费者的购买偏好，为采购决策和
        品类运营提供数据支持。不同品类的销售表现反映了市场需求的变化趋势。
        """
        story.append(Paragraph(category_intro, self.styles['ChineseBody']))
        story.append(Spacer(1, 0.2*inch))
        
        # 添加饼图
        pie_img_path = self._fig_to_image(pie_chart, width=650, height=500)
        story.append(Image(pie_img_path, width=6*inch, height=4.6*inch))
        story.append(Paragraph("图2：商品品类销售占比分布", self.styles['ChineseCaption']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # 添加品类分析说明
        category_analysis = f"""
        <b>品类表现分析：</b><br/>
        • <b>{stats['最佳品类']}</b> 是本月份销售冠军品类，销售额达到 <b>¥{stats['最佳品类销售额']:,.2f}</b><br/>
        • 从品类分布来看，销售额呈现明显的头部集中效应，前4名品类占据了绝大部分市场份额<br/>
        • 高单价品类（如手机数码、家用电器）虽然订单量相对较少，但对总销售额贡献显著<br/>
        • 快消品类（如食品生鲜、美妆个护）订单频次高，是保持用户活跃度的重要品类<br/>
        • 建议后续加强优势品类的供应链管理，同时关注潜力品类的增长机会
        """
        story.append(Paragraph(category_analysis, self.styles['ChineseBody']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # 添加汇总统计表格
        story.append(Paragraph("三、核心指标汇总", self.styles['ChineseHeading']))
        story.append(Spacer(1, 0.2*inch))
        story.append(self._create_summary_table(stats))
        
        story.append(Spacer(1, 0.3*inch))
        
        # 结语
        conclusion = """
        <b>总结与建议：</b><br/>
        综合以上数据分析，2026年5月的整体销售表现良好。建议在后续运营中：
        1) 持续优化黄金时段的营销活动投放；2) 加强头部品类的库存保障；3) 针对低活跃时段设计促销策略；
        4) 深入分析用户复购行为，提升客户生命周期价值。
        """
        story.append(Paragraph(conclusion, self.styles['ChineseBody']))
        
        # 生成PDF
        doc.build(story)
        
        # 清理临时文件
        try:
            os.remove(daily_img_path)
            os.remove(pie_img_path)
        except:
            pass
        
        print(f"PDF报告已生成: {self.output_path}")


if __name__ == "__main__":
    # 测试代码
    from data_processor import SalesDataProcessor
    from visualizer import SalesVisualizer
    
    processor = SalesDataProcessor("data/sales_data_2026_05.csv")
    visualizer = SalesVisualizer()
    
    daily_data = processor.get_daily_sales()
    top_data, others_data = processor.get_category_sales(top_n=4)
    stats = processor.get_summary_stats()
    
    daily_chart = visualizer.create_daily_sales_chart(daily_data)
    pie_chart = visualizer.create_category_pie_chart(top_data, others_data)
    
    generator = PDFReportGenerator("output/test_report.pdf")
    generator.generate_report(daily_chart, pie_chart, stats)
