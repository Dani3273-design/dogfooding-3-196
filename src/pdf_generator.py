from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import io
from pathlib import Path

def register_fonts():
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

def create_pdf_report(output_path: str, daily_chart_img: bytes, category_chart_img: bytes, stats: dict) -> None:
    register_fonts()
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='STSong-Light',
        fontSize=20,
        spaceAfter=30,
        alignment=1,
        textColor=colors.HexColor("#333333")
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontName='STSong-Light',
        fontSize=14,
        spaceAfter=25,
        alignment=1,
        textColor=colors.HexColor("#666666")
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName='STSong-Light',
        fontSize=16,
        spaceAfter=15,
        textColor=colors.HexColor("#2980b9")
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName='STSong-Light',
        fontSize=11,
        spaceAfter=12,
        leading=18,
        textColor=colors.HexColor("#555555")
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='STSong-Light',
        fontSize=11,
        alignment=1,
        textColor=colors.white
    )
    
    table_style = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='STSong-Light',
        fontSize=10,
        alignment=1
    )
    
    story = []
    
    story.append(Paragraph("电商销售数据分析报告", title_style))
    story.append(Paragraph(f"数据周期：2026年5月", subtitle_style))
    
    story.append(Paragraph("一、数据概览", heading_style))
    
    overview_text = """
    本报告基于2026年5月全月的电商销售数据进行深度分析。数据涵盖了手机数码、家用电器、服装鞋包、食品生鲜、美妆个护、家居家装、母婴用品、运动户外等八大核心商品品类，共计{}条有效订单记录。
    通过对销售数据的多维度透视，我们将从每日销售趋势、商品品类结构两个核心维度进行数据可视化呈现，为业务决策提供数据支撑。
    """.format(stats["订单总数"])
    
    story.append(Paragraph(overview_text, normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    table_data = [
        [Paragraph("指标名称", table_header_style), Paragraph("数值", table_header_style), 
         Paragraph("指标名称", table_header_style), Paragraph("数值", table_header_style)],
        [Paragraph("总销售额", table_style), Paragraph(f"¥ {stats['总销售额']:,.2f}", table_style),
         Paragraph("订单总数", table_style), Paragraph(f"{stats['订单总数']} 笔", table_style)],
        [Paragraph("客单价", table_style), Paragraph(f"¥ {stats['客单价']:,.2f}", table_style),
         Paragraph("独立用户数", table_style), Paragraph(f"{stats['独立用户数']} 人", table_style)],
        [Paragraph("销售峰值日", table_style), Paragraph(f"{stats['销售峰值日']}", table_style),
         Paragraph("峰值日销售额", table_style), Paragraph(f"¥ {stats['峰值日销售额']:,.2f}", table_style)],
        [Paragraph("最畅销品类", table_style), Paragraph(f"{stats['最畅销品类']}", table_style),
         Paragraph("品类贡献额", table_style), Paragraph(f"¥ {stats['最畅销品类销售额']:,.2f}", table_style)]
    ]
    
    table = Table(table_data, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2980b9")),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#dee2e6")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph("二、每日销售趋势分析", heading_style))
    
    daily_text = """
    下图展示了2026年5月全月每日销售金额的变化趋势。通过柱状图与趋势线的结合，可以清晰观察到整月销售波动的整体态势。
    从时间维度看，周末通常呈现较高的消费活跃度，而月中促销期也可能带来明显的销售峰值。此外，节假日效应、营销活动投放、季节性商品热销等因素均会对日销数据产生显著影响。
    建议重点关注销售低谷期的原因排查，以及高峰日的成功经验总结，为后续运营策略优化提供参考。
    """
    story.append(Paragraph(daily_text, normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    daily_img = Image(io.BytesIO(daily_chart_img), width=17*cm, height=10*cm)
    story.append(daily_img)
    story.append(Spacer(1, 0.5*cm))
    
    daily_insight = """
    <b>分析洞察：</b>从数据中可以看出，每周的销售高峰通常出现在特定时段，这与消费者的购物习惯高度相关。
    建议运营团队可在销售高峰到来前做好库存准备与人员配置，同时在销售低谷期可适当推出促销活动以拉动消费。
    """
    story.append(Paragraph(daily_insight, normal_style))
    
    story.append(PageBreak())
    
    story.append(Paragraph("三、商品品类结构分析", heading_style))
    
    category_text = """
    下图展示了各商品品类的销售金额占比情况。为便于可视化呈现，我们选取了销售总金额排名前4的核心品类，其余品类统一归为"其他"类别。
    品类结构分析能够帮助我们清晰识别当前的核心利润来源与潜力增长品类。通常，高客单价品类（如手机数码、家用电器）在销售金额贡献上占据较大比重，而高频消费品类（如服装鞋包、食品生鲜）则凭借订单量优势也占据重要位置。
    """
    story.append(Paragraph(category_text, normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    category_img = Image(io.BytesIO(category_chart_img), width=16*cm, height=10*cm)
    story.append(category_img)
    story.append(Spacer(1, 0.5*cm))
    
    category_insight = """
    <b>品类策略建议：</b>
    <br/>1. <b>核心品类</b>：对于销售额占比最高的品类，应继续强化供应链优势，确保供货稳定与价格竞争力；
    <br/>2. <b>潜力品类</b>：对于销售额占比快速提升的品类，可考虑增加营销资源投入，挖掘增长潜力；
    <br/>3. <b>长尾品类</b>：对于归为"其他"类别的品类，可进行精细化运营评估，优胜劣汰优化品类结构。
    """
    story.append(Paragraph(category_insight, normal_style))
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph("四、总结与建议", heading_style))
    
    summary_text = """
    综合以上分析，我们对2026年5月的销售运营提出以下建议：
    
    1. <b>时间维度优化</b>：针对销售高峰时段提前备货，低谷期策划主题营销活动；
    2. <b>品类结构优化</b>：聚焦核心品类深耕细作，同时积极培育高潜力新兴品类；
    3. <b>用户运营优化</b>：结合用户购买行为数据开展精准营销，提升复购率与客单价；
    4. <b>数据驱动决策</b>：建立常态化销售监测机制，实现数据驱动的精细化运营。
    
    通过数据分析驱动业务增长，将是电商运营的核心竞争力所在。建议持续跟踪关键销售指标，不断优化运营策略。
    """
    story.append(Paragraph(summary_text, normal_style))
    story.append(Spacer(1, 2*cm))
    
    story.append(Paragraph("—— 报告完 ——", ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontName='STSong-Light',
        fontSize=12,
        alignment=1,
        textColor=colors.HexColor("#999999")
    )))
    
    doc.build(story)
    print(f"PDF report generated: {output_path}")
