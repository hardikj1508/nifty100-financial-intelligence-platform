import streamlit as st
import pandas as pd
from pathlib import Path

from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)
from reportlab.graphics.shapes import(
    Drawing,
    Rect,
    String,
    Line
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "tearsheet_ template.pdf"

FINANCIAL_RATIO_FILE = DATA_DIR / "financial_ratios_clean.csv"
PROFIT_LOSS_FILE = DATA_DIR / "profitandloss_clean.csv"
COMPANIES_FILE = DATA_DIR / "companies_clean.csv"
BALANCE_SHEET_FILE = DATA_DIR / "balancesheet_clean.csv"
CASH_FLOW_FILE = DATA_DIR / "cashflow_clean.csv"

PAGE_WIDTH, PAGE_HEIGHT = A4

MARGIN_LEFT = 35
MARGIN_RIGHT = 35
MARGIN_TOP = 35
MARGIN_BOTTOM = 35

NAVY = colors.HexColor("#172554")
LIGHT_BLUE = colors.HexColor("#EFF6FF")
LIGHT_GREY = colors.HexColor("#F3F4F6")
DARK_GREY = colors.HexColor("#374151")

GREEN = colors.HexColor("#15803d")
LIGHT_GREEN = colors.HexColor("#DCFCE7")

RED = colors.HexColor("#B91C1C")
LIGHT_RED = colors.HexColor("#FEE2E2")

WHITE = colors.white


styles = getSampleStyleSheet()

company_styles = ParagraphStyle(
    "CompanyName",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=18,
    textColor=WHITE,
)

ticker_style = ParagraphStyle(
    "Ticker",
    parent=styles["Normal"],
    fontName='Helvetica',
    fontSize=10,
    textColor=colors.HexColor("#D1D5DB"),
)

section_style = ParagraphStyle(
    "Section",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=11,
    textColor=NAVY,
    spaceAfter=6,
)

placeholder_style = ParagraphStyle(
    "Placeholder",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    textColor=DARK_GREY,
    alignment=TA_CENTER
)

bullet_style = ParagraphStyle(
    "Bullet",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    textColor=DARK_GREY,
    leftIndent=12,
    leading=13,
)

def create_header(company_name, ticker):
    header_data = [
        [
            Paragraph(company_name, company_styles),
            Paragraph(ticker, ticker_style)
        ]
    ]

    header = Table(
        header_data,
        colWidths=[PAGE_WIDTH - 160, 90],
        rowHeights = [45]
    )

    header.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )

    return header

def create_kpi_tiles(data):

    kpis = [
        (
            "Revenue",
            f"₹{data['revenue']:,.0f}"
        ),
        (
            "Net Profit",
            f"₹{data['net_profit']:,.0f}"
        ),
        (
            "Net Margin",
            f"{data['net_margin']:.2f}%"
        ),
        (
            "ROE",
            f"{data['roe']:.2f}%"
        ),
        (
            "ROCE",
            f"{data['roce']:.2f}%"
        ),
        (
            "Debt / Equity",
            f"{data['debt_to_equity']:.2f}x"
        ),
    ]

    cells = []

    for name, value in kpis:

        cell = Table(
            [
                [
                    Paragraph(
                        name,
                        ParagraphStyle(
                            "KPIName",
                            parent=styles["Normal"],
                            fontName="Helvetica-Bold",
                            fontSize=8,
                            textColor=DARK_GREY,
                        )
                    )
                ],
                [
                    Paragraph(
                        value,
                        ParagraphStyle(
                            "KPIValue",
                            parent=styles["Normal"],
                            fontName="Helvetica-Bold",
                            fontSize=13,
                            textColor=NAVY,
                        )
                    ),
                ],
            ],
            colWidths=155,
            rowHeights=[18, 27],
        )

        cell.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#CBD5E1")
                    ),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        cells.append(cell)

    kpi_table = Table(
        [
            cells[0:3],
            cells[3:6],
        ],
        colWidths=[170, 170, 170],
        rowHeights=[52, 52],
        hAlign="CENTER",
    )

    kpi_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    return kpi_table

def chart_placeholder(title, height=150):

    content = Table(
        [
            [
                Paragraph(
                    f"{title}<br/><br/>Chart will be added in Phase 2",
                    placeholder_style,
                )
            ],
        ],
        colWidths=[250],
        rowHeights=[height],
    )

    content.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY),
                ("BOX", (0, 0),(-1, -1),0.7, colors.HexColor("#9CA3AF")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )

    return content

def bullet_section(title, bullets,background, title_color):

    rows = [
        [
            Paragraph(
                title,
                ParagraphStyle(
                    "BulletTitle",
                    parent=styles["Normal"],
                    fontName="Helvetica-Bold",
                    textColor=title_color,
                )
            ),
        ]
    ]

    for item in bullets:

        rows.append(
            [
                Paragraph(
                    f"• {item}",
                    bullet_style,
                )
            ]
        )
    table = Table(
        rows,
        colWidths=[500],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 0.5, title_color),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                
            ]
        )
    )

    return table

def capital_allocation_badge(data):
    """
    Create a dynamic capital allocation assessment
    """

    financial = data["financial_history"].sort_values("year").copy()
    latest = financial.iloc[-1]

    def safe_float(value):
        try:
            if pd.isna(value):
                return None
            return float(value)
        except (ValueError, TypeError):
            return None

    debt_equity = safe_float(
        latest.get("debt_to_equity")
    )
    dividend_payout = safe_float(
        latest.get("dividend_payout_ratio")
    )
    roe = safe_float(
        latest.get("return_on_equity_pct")
    )
    free_cash_flow = safe_float(
        latest.get("free_cash_flow_cr")
    )

    score = 0
    total = 0

    #DEBT / EQUITY

    if debt_equity is not None:
        total +=1

        if debt_equity < 0.5:
            score += 1

    #ROE

    if roe is not None:
        total += 1

        if roe>= 15:
            score += 1

    #Dividend payout

    if dividend_payout is not None:
        total += 1

        if 20 <= dividend_payout <= 70:
            score += 1

    #Free cash flow

    if free_cash_flow is not None:
        total += 1

        if free_cash_flow > 0:
            score += 1

# ---------------------------------------------------------
# OVERALL ASSESSMENT
# ---------------------------------------------------------

    if total == 0:
        assessment = "INSUFFICIENT DATA"
        badge_color = colors.HexColor("#757575")

    elif score / total >= 0.75:
        assessment = "STRONG"
        badge_color = colors.HexColor("#2E7D32")

    elif score / total >= 0.50:
        assessment = "MODERATE"
        badge_color = colors.HexColor("#F57C00")

    else:
        assessment = "WEAK"
        badge_color = colors.HexColor("#C62828")

    #Badge

    badge_label_style = ParagraphStyle(
        "CapitalLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=NAVY,
        alignment=1,
    )

    badge_value_style = ParagraphStyle(
        "CapitalValue",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        textColor=colors.white,
        alignment=1,
    )

    badge = Table(
        [
            [
                Paragraph(
                    "CAPITAL ALLOCATION",
                    badge_label_style
                )
            ],
            [
                Paragraph(
                    assessment,
                    badge_value_style
                )
            ],
        ],
        colWidths=[190],
        rowHeights=[25, 35],
    )

    badge.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    LIGHT_BLUE,
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, 1),
                    badge_color,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    badge_color,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )
    colWidths=[190],
    rowHeights=[25, 35],
    

    badge.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), LIGHT_BLUE),
                ("BACLGROUND", (0, 1), (-1, 1), badge_color),
                ("BOX", (0, 0), (-1, -1), 0.7, badge_color),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE",),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6)
            ]
        )
    )

    #Supporting metrics

    metrics = []

    if debt_equity is not None:
        metrics.append(
            f"Debt/Equity: {debt_equity:.2f}x"
        )

    if roe is not None:
        metrics.append(
            f"ROE: {roe:.1f}%"
        )
    if dividend_payout is not None:
        metrics.append(
            f"Dividend Payout: {dividend_payout:.1f}%"
        )
    if free_cash_flow is not None:
        metrics.append(
            f"Free Cash Flow: {free_cash_flow:.0f}"
        )

    metric_paragraphs = []

    for metric in metrics:
        metric_paragraphs.append(
            Paragraph(
                f"• {metric}",
                ParagraphStyle(
                    "CapitalMetric",
                    parent=styles["Normal"],
                    fontName="Helvetica",
                    fontSize=7.5,
                    leading=10,
                    textColor=DARK_GREY,
            )
        )
        )

    metric_table = Table(
        [[metric] for metric in metric_paragraphs],
        colWidths=[190],
    )

    metric_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    colors.HexColor("#F7F9FC"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#CBD5E1"),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    return Table(
        [[badge, metric_table]],
        colWidths=[200, 200],
        rowHeights=[70],
    )

def load_company_data(company_id):

    financial = pd.read_csv(FINANCIAL_RATIO_FILE)
    balance_sheet = pd.read_csv(BALANCE_SHEET_FILE)
    profit_loss = pd.read_csv(PROFIT_LOSS_FILE)
    companies = pd.read_csv(COMPANIES_FILE)
    cash_flow = pd.read_csv(CASH_FLOW_FILE)

    financial = financial[
        financial["company_id"] == company_id
    ].copy()

    cash_flow = cash_flow[
        cash_flow["company_id"] == company_id
    ].copy()

    cash_flow = cash_flow.sort_values("year")

    balance_sheet = balance_sheet[
        balance_sheet["company_id"] == company_id
    ].copy()

    latest_financial = financial.iloc[-1]

    profit_loss = profit_loss[
        profit_loss["company_id"] == company_id
    ].copy()

    profit_loss = profit_loss.sort_values("year")

    if profit_loss.empty:
        raise ValueError(
            f"No profit & loss data found for {company_id}"
        )

    latest_profit_loss = profit_loss.iloc[-1]

    company = companies[
        companies["id"] == company_id
    ].copy()

    if company.empty and "company_id" in companies.columns:
        company = companies[
            companies["company_id"] == company_id
        ].copy()

    if company.empty:
        raise ValueError(
            f"No company information found for {company_id}"
        )

    latest_company = company.iloc[-1]

    financial_history = financial.merge(
        balance_sheet[
            [
                "company_id",
                "year",
                "equity_capital",
                "reserves",
                "borrowings",
                "other_liabilities",
            ]
        ],
        on=["company_id", "year"],
        how="left",
    )

    return {
        "company_id": company_id,

        "company_name": latest_company["company_name"],

        "ticker": company_id,

        "revenue": latest_profit_loss["sales"],

        "net_profit": latest_profit_loss["net_profit"],

        "net_margin": latest_financial[
            "net_profit_margin_pct"
        ],

        "roe": latest_financial[
            "return_on_equity_pct"
        ],

        "roce": latest_company[
            "roce_percentage"
        ],

        "debt_to_equity": latest_financial[
            "debt_to_equity"
        ],

        "profit_loss_history": profit_loss,

        "financial_history": financial_history,

        "cash_flow_history": cash_flow,
    }

def create_financial_bar_chart(history, column, title):
    """
    Create a 10-period vertical bar chart.
    
    Parameters
    ----------
    history : pandas.DataFrame
        Historical company financial data.
        
    column : str
        Financial column to plot.
    
    title : str
        Chart title.
    """

    history = history.copy()

    # Sort chronologically
    history = history.sort_values("year")

    # Keep the latest 10 available periods
    history = history.tail(10)

    # Convert labels to stings
    labels = history["year"].astype(str).tolist()

    values = (
        pd.to_numeric(
            history[column],
            errors="coerce"
        )
        .fillna(0)
        .tolist()
    )

    drawing = Drawing(250, 190)

    chart = VerticalBarChart()

    chart.x = 35
    chart.y = 35

    chart.width = 205
    chart.height = 125

    chart.data = [values]

    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 7
    chart.categoryAxis.labels.angle = 0

    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 7

    chart.valueAxis.valueMin = 0

    chart.barWidth = 12

    chart.groupSpacing = 10

    chart.strokeColor = colors.HexColor("#CBD5E1")

    chart.valueAxis.strokeColor = colors.HexColor("#94A3B8")
    chart.categoryAxis.strokeColor = colors.HexColor("#94A3B8")

    drawing.add(chart)

    return drawing

def create_roe_chart(history):
    """
    Create a historical ROE line chart.
    """

    history = history.copy()

    history = history = history.sort_values("year").tail(10)

    labels = history["year"].astype(str).tolist()

    values = (
        pd.to_numeric(
            history["return_on_equity_pct"],
            errors="coerce"
        )
        .fillna(0)
        .tolist()
    )

    drawing = Drawing(470, 190)

    chart = HorizontalLineChart()

    chart.x = 45
    chart.y = 35

    chart.width = 400
    chart.height = 125

    chart.data = [values]

    chart.categoryAxis.categoryNames = labels

    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize =7

    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 7

    chart.valueAxis.valueMin = 0

    chart.valueAxis.valueMax = max(values) + 10

    chart.lines[0].strokeWidth = 2

    drawing.add(chart)

    return drawing

def create_balance_sheet_chart(history):
    """
    Crete a stacked bar chart showing balance sheet composition
    across the latest 10 periods
    """

    history = history.copy()

    history = history.sort_values("year").tail(10)

    labels = history["year"].astype(str).tolist()

    equity = (
        pd.to_numeric(history["equity_capital"], errors="coerce")
        .fillna(0)
        .tolist()
    )

    reserves = (
        pd.to_numeric(history["breserves"], errors="coerce")
        .fillna(0)
        .tolist()
    )

    borrowings = (
        pd.to_numeric(history["borrowings"], errors="coerce")
        .fillna(0)
        .tolist()
    )

    other_liabilities = (
        pd.to_numeric(history["other_liabilities"], error="coerce")
        .fillna(0)
        .tolist()
    )

    drawing = Drawing(470, 220)

    chart = VerticalBarChart()

    chart.x = 45
    chart.y = 45

    chart.width = 400
    chart.height = 145

    chart.data = [
        equity,
        reserves,
        borrowings,
        other_liabilities
    ]

    chart.categoryAxis.style = "stacked"

    chart.categoryAxis.categoryNames = labels

    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 7

    chart.valueAxis.labels.fontName = "Helvitica"
    chart.valueAxis.labels.fontSize = 7

    chart.valueAxis.valueMin = 0

    chart.barWidth = 18
    chart.groupSpacing = 10

    chart.barSpacing = 0

    chart.bars[0].fillColor = NAVY
    chart.bars[1].fillColor = colors.HexColor("#5B8FF9")
    chart.bars[2].fillColor = colors.HexColor("#F5A623")
    chart.bars[3].fillColor = colors.HexColor("#7CB342")

    drawing.add(chart)

    return drawing

def create_balance_sheet_chart(history):
    """
    Crete a 10-year stacked bar chart showing
    balance sheet composition.
    """

    history = history.copy()

    history = history.sort_values("year").tail(10)

    years = history["year"].astype(str).tolist()

    equity = (
        pd.to_numeric(history["equity_capital"], errors="coerce")
        .fillna(0)
        .tolist()
    )

    reserves = (
        pd.to_numeric(history["reserves"], errors="coerce")
        .fillna(0)
        .tolist()
    )

    borrowings = (
        pd.to_numeric(history["borrowings"], errors="coerce")
        .fillna(0)
        .tolist()
    )

    other_liabilities = (
        pd.to_numeric(history["other_liabilities"], errors="coerce")
        .fillna(0)
        .tolist()
    )

    drawing = Drawing(470, 190)

    chart = VerticalBarChart()

    chart.x = 45
    chart.y = 45

    chart.width = 400
    chart.height = 145

    chart.data = [
        equity,
        reserves,
        borrowings,
        other_liabilities
    ]

    chart.categoryAxis.style = "stacked"

    chart.categoryAxis.categoryNames = years

    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 7

    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 7

    chart.valueAxis.valueMin = 0

    chart.barWidth = 18
    chart.groupSpacing = 10

    drawing.add(chart)

    return drawing

def create_cash_flow_waterfall(history):
    """
    Create a proper cash-flow waterfall for the latest year.
    
    Shows:
    CFO → CFI → CFF → Net cash Flow 
    """

    history = history.copy()
    history = history.sort_values("year")

    latest = history.iloc[-1]

    cfo = float(latest["operating_activity"])
    cfi = float(latest["investing_activity"])
    cff = float(latest["financing_activity"])
    net_cash = float(latest["net_cash_flow"])

    #Runnung Totals

    start_cfo = 0
    end_cfo = cfo

    start_cfi = end_cfo
    end_cfi = end_cfo + cfi

    start_cff = end_cfi
    end_cff = end_cfi + cff

    #Chart Dimensions

    width = 470
    height = 160
    left = 45
    bottom = 35
    chart_width = 390
    chart_height = 145

    drawing = Drawing(width, height)

    #Determine scale


    all_values = [
        0,
        end_cfo,
        end_cfi,
        end_cff,
        net_cash
    ]

    min_value = min(all_values)
    max_value = max(all_values)

    padding = (max_value - min_value) * 0.15

    if padding == 0:
        padding =1

    y_min = min_value - padding
    y_max = max_value + padding

    def y(value):
        return bottom + (
            (value - y_min)
            / (y_max - y_min)
        ) * chart_height

    #Baseline

    zero_y = y(0)

    drawing.add(
        Line(
            left,
            zero_y,
            left + chart_width,
            zero_y,
            strokeColor=colors.HexColor("#777777"),
            strokeWidth=0.7
        )
    )

    #Bar configuration

    labels = [
        "CFO",
        "CFI",
        "CFF",
        "Net Cash Flow"
    ]

    bar_values = [
        cfo,
        cfi,
        cff,
        net_cash
    ]

    bar_bottoms = [
        start_cfo,
        start_cfi,
        start_cff,
        0
    ]

    bar_tops = [
        end_cfo,
        end_cfi,
        end_cff,
        net_cash
    ]

    bar_width = 55
    spacing = 40

    x_positions = [
        left + 25,
        left + 25 + bar_width + spacing,
        left + 25 + 2 * (bar_width + spacing),
        left + 25 + 3 * (bar_width + spacing)
    ]

    #Draw Waterfall bars

    for i in range(4):

        value = bar_values[i]
        bar_bottom = bar_bottoms[i]
        bar_top = bar_tops[i]

        y_bottom = y(min(bar_bottom, bar_top))
        y_top = y(max(bar_bottom, bar_top))

        bar_height = y_top - y_bottom

        if i == 3:
            #Final net cash total
            fill = NAVY
        elif value >= 0:
            fill = colors.HexColor("#7CB342")
        else:
            fill = colors.HexColor("#D9534F")


        drawing.add(
            Rect(
                x_positions[i],
                y_bottom,
                bar_width,
                bar_height,
                fillColor=fill,
                strokeColor=colors.HexColor("#333333"),
                strokeWidth = 0.6
            )
        )

        #Value label

        label_y = y_top + 5

        if value < 0:
            label_y = y_bottom - 13

        drawing.add(
            String(
                x_positions[i] + bar_width / 2,
                label_y,
                f"{value:,.0f}",
                fontName="Helvetica-Bold",
                fontSize = 7
            )
        )

        #Category label

        drawing.add(
            String(
                x_positions[i] + bar_width / 2,
                bottom - 15,
                labels[i],
                fontName="Helvetica-Bold",
                fontSize = 7,
                textAnchor="middle",
                fillColor=colors.HexColor("#222222")
            )
        )

    #Connector Lines

    connector_color = colors.HexColor("#888888")

    #CFO → CFI
    drawing.add(
        Line(
            x_positions[0] + bar_width,
            y(end_cfo),
            x_positions[1],
            y(end_cfo),
            strokeColor=connector_color,
            strokeWidth=0.6
        )
    )

    #CFI → CFF
    drawing.add(
        Line(
            x_positions[1] + bar_width,
            y(end_cfi),
            x_positions[2],
            y(end_cfi),
            strokeColor=connector_color,
            strokeWidth=0.6
        )
    )

    #CFF → Net Cash Flow
    drawing.add(
        Line(
            x_positions[2] + bar_width,
            y(end_cff),
            x_positions[3],
            y(net_cash),
            strokeColor=connector_color,
            strokeWidth=0.6
        )
    )

    return drawing

def create_pros_cons_section(data):
    """
    Generate a dynamic Investment View based on the company's
    latest financial and cash-flow data.
    """

    financial = data["financial_history"].sort_values("year").copy()
    latest = financial.iloc[-1]

    cash_flow = data.get("cash_flow_history")

    pros = []
    cons = []

    # ---------------------------------------------------------
    # HELPER
    # ---------------------------------------------------------
    def safe_float(value):
        try:
            if pd.isna(value):
                return None
            return float(value)
        except (ValueError, TypeError):
            return None

    # ---------------------------------------------------------
    # LATEST FINANCIAL METRICS
    # ---------------------------------------------------------
    roe = safe_float(latest.get("return_on_equity_pct"))
    debt_equity = safe_float(latest.get("debt_to_equity"))
    net_margin = safe_float(latest.get("net_profit_margin_pct"))
    operating_margin = safe_float(
        latest.get("operating_profit_margin_pct")
    )

    # ---------------------------------------------------------
    # PROFITABILITY
    # ---------------------------------------------------------
    if roe is not None:
        if roe >= 20:
            pros.append(f"Strong ROE of {roe:.1f}%")
        elif roe >= 15:
            pros.append(f"Healthy ROE of {roe:.1f}%")
        elif roe < 10:
            cons.append(f"Low ROE of {roe:.1f}%")

    if net_margin is not None:
        if net_margin >= 15:
            pros.append(f"Strong net margin of {net_margin:.1f}%")
        elif net_margin < 10:
            cons.append(f"Low net margin of {net_margin:.1f}%")

    if operating_margin is not None:
        if operating_margin >= 15:
            pros.append(
                f"Healthy operating margin of {operating_margin:.1f}%"
            )
        elif operating_margin < 10:
            cons.append(
                f"Low operating margin of {operating_margin:.1f}%"
            )

    # ---------------------------------------------------------
    # DEBT
    # ---------------------------------------------------------
    if debt_equity is not None:
        if debt_equity < 0.5:
            pros.append(
                f"Low financial leverage (Debt/Equity {debt_equity:.2f}x)"
            )
        elif debt_equity > 1:
            cons.append(
                f"High financial leverage (Debt/Equity {debt_equity:.2f}x)"
            )

    # ---------------------------------------------------------
    # CASH FLOW
    # ---------------------------------------------------------
    if cash_flow is not None and not cash_flow.empty:

        cash_flow = cash_flow.sort_values("year")
        latest_cf = cash_flow.iloc[-1]

        cfo = safe_float(latest_cf.get("operating_activity"))
        cfi = safe_float(latest_cf.get("investing_activity"))
        cff = safe_float(latest_cf.get("financing_activity"))
        net_cash = safe_float(latest_cf.get("net_cash_flow"))

        if cfo is not None:
            if cfo > 0:
                pros.append(
                    f"Positive operating cash flow of {cfo:,.0f}"
                )
            elif cfo < 0:
                cons.append(
                    "Negative operating cash flow"
                )

        if cfi is not None and cfi < 0:
            pros.append(
                "Investment outflow indicates continued capital deployment"
            )

        if cff is not None and cff < 0:
            cons.append(
                "Negative financing cash flow"
            )

        if net_cash is not None:
            if net_cash > 0:
                pros.append(
                    f"Positive net cash flow of {net_cash:,.0f}"
                )
            elif net_cash < 0:
                cons.append(
                    "Negative net cash flow"
                )

    # ---------------------------------------------------------
    # REVENUE / PROFIT TREND
    # ---------------------------------------------------------
    profit_loss = data.get("profit_loss_history")

    if profit_loss is not None and not profit_loss.empty:

        profit_loss = profit_loss.sort_values("year")

        if len(profit_loss) >= 2:

            first = profit_loss.iloc[0]
            last = profit_loss.iloc[-1]

            first_sales = safe_float(first.get("sales"))
            last_sales = safe_float(last.get("sales"))

            first_profit = safe_float(first.get("net_profit"))
            last_profit = safe_float(last.get("net_profit"))

            if (
                first_sales is not None
                and last_sales is not None
                and last_sales > first_sales
            ):
                pros.append("Long-term revenue growth")

            if (
                first_profit is not None
                and last_profit is not None
                and last_profit > first_profit
            ):
                pros.append("Long-term net profit growth")

    # ---------------------------------------------------------
    # LIMIT NUMBER OF ITEMS
    # ---------------------------------------------------------
    pros = pros[:5]
    cons = cons[:5]

    # Fallbacks
    if not pros:
        pros.append("No major positive indicator identified")

    if not cons:
        cons.append("No major negative indicator identified")

    # ---------------------------------------------------------
    # STYLES
    # ---------------------------------------------------------
    bullet_style = ParagraphStyle(
        "InvestmentBullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=DARK_GREY,
        spaceAfter=4,
    )

    header_style_pro = ParagraphStyle(
        "ProsHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.HexColor("#2E7D32"),
    )

    header_style_con = ParagraphStyle(
        "ConsHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.HexColor("#D32F2F"),
    )

    # ---------------------------------------------------------
    # CREATE PROS CONTENT
    # ---------------------------------------------------------
    pros_content = [
        [
            Paragraph("Pros", header_style_pro)
        ]
    ]

    for item in pros:
        pros_content.append(
            [
                Paragraph(
                    f"• {item}",
                    bullet_style
                )
            ]
        )

    # ---------------------------------------------------------
    # CREATE CONS CONTENT
    # ---------------------------------------------------------
    cons_content = [
        [
            Paragraph("Cons", header_style_con)
        ]
    ]

    for item in cons:
        cons_content.append(
            [
                Paragraph(
                    f"• {item}",
                    bullet_style
                )
            ]
        )

    # ---------------------------------------------------------
    # INDIVIDUAL TABLES
    # ---------------------------------------------------------
    pros_table = Table(
        pros_content,
        colWidths=[190]
    )

    pros_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#E8F5E9"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#A5D6A7"),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    cons_table = Table(
        cons_content,
        colWidths=[190]
    )

    cons_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#FFEBEE"),
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor("#EF9A9A"),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    # ---------------------------------------------------------
    # SIDE-BY-SIDE LAYOUT
    # ---------------------------------------------------------
    investment_view = Table(
        [
            [
                pros_table,
                cons_table
            ]
        ],
        colWidths=[195, 195]
    )

    investment_view.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    0,
                ),
            ]
        )
    )

    return [
        Paragraph(
            "Investment View",
            section_style
        ),
        Spacer(1, 8),
        investment_view,
    ]

def build_tearsheet(company_id="TCS"):

    # ============================================================
    # LOAD COMPANY DATA
    # ============================================================

    data = load_company_data(company_id)

    company_name = data["company_name"]
    ticker = data["ticker"]

    # ============================================================
    # DOCUMENT
    # ============================================================

    doc = SimpleDocTemplate(
        str(OUTPUT_FILE),
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
    )

    story = []

    # ============================================================
    # PAGE 1 — HEADER
    # ============================================================

    story.append(
        Table(
            [
                [
                    Paragraph(
                        company_name,
                        ParagraphStyle(
                            "CompanyName",
                            parent=styles["Normal"],
                            fontName="Helvetica-Bold",
                            fontSize=20,
                            textColor=colors.white,
                        ),
                    ),
                    Paragraph(
                        ticker,
                        ParagraphStyle(
                            "Ticker",
                            parent=styles["Normal"],
                            fontName="Helvetica",
                            fontSize=11,
                            textColor=colors.white,
                            alignment=TA_RIGHT,
                        ),
                    ),
                ]
            ],
            colWidths=[400, 70],
            rowHeights=[60],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (0, 0), 18),
                    ("RIGHTPADDING", (-1, 0), (-1, 0), 18),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            ),
        )
    )

    story.append(Spacer(1, 12))

    # ============================================================
    # KEY PERFORMANCE INDICATORS
    # ============================================================

    story.append(
        Paragraph(
            "Key Performance Indicators",
            section_style,
        )
    )

    story.append(
        create_kpi_tiles(data)
    )

    story.append(Spacer(1, 12))

    # ============================================================
    # REVENUE & NET PROFIT — 10 YEAR TREND
    # ============================================================

    story.append(
        Paragraph(
            "Revenue & Net Profit - 10 Year Trend",
            section_style,
        )
    )

    history = data["profit_loss_history"].copy()

    # Revenue chart
    revenue_chart = create_financial_bar_chart(
        history,
        "sales",
        "10-Year Revenue",
    )

    # Net profit chart
    profit_chart = create_financial_bar_chart(
        history,
        "net_profit",
        "10-Year Net Profit",
    )

    # Place both charts side-by-side
    revenue_profit = Table(
        [
            [
                revenue_chart,
                profit_chart,
            ]
        ],
        colWidths=[235, 235],
        rowHeights=[190],
    )

    revenue_profit.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),

                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(revenue_profit)



    # ============================================================
    # ROE HISTORICAL TREND
    # ============================================================

    story.append(
        Paragraph(
            "Return on Equity - Historical Trend",
            section_style,
        )
    )

    roe_chart = create_roe_chart(
        data["financial_history"]
    )

    story.append(roe_chart)

    story.append(Spacer(1, 12))

    # ============================================================
    # PAGE 2
    # ============================================================

    story.append(PageBreak())

    # ============================================================
    # BALANCE SHEET COMPOSITION
    # ============================================================

    story.append(
        Paragraph(
            "Balance Sheet Composition",
            section_style,
        )
    )

    balance_sheet_chart = create_balance_sheet_chart(
        data["financial_history"]
    )

    story.append(balance_sheet_chart)

    story.append(Spacer(1, 12))

    story .append(
        Paragraph(
            "Cash Flow - Latest Year",
            section_style
        )
    )

    cash_flow_waterfall = create_cash_flow_waterfall(
        data["cash_flow_history"]
    )

    story.append(cash_flow_waterfall)

    story.append(Spacer(1, 12))

    story.extend(
        create_pros_cons_section(data)
    )

    capital_allocation_section = KeepTogether(
        [
            Spacer(1, 12),

            Paragraph(
                "Capital Allocation",
                section_style
            ),

            Spacer(1, 8),

            capital_allocation_badge(data),

            Spacer(1, 12),
        ]
    )

    story.append(capital_allocation_section)
    

    # ------------------------------------------------------------
    # KEEP YOUR EXISTING PAGE 2 CODE HERE
    # ------------------------------------------------------------
    #
    # Balance Sheet Composition
    # Cash Flow Waterfall
    # Pros
    # Cons
    # Capital Allocation Badge
    #
    # ------------------------------------------------------------

    # ============================================================
    # BUILD PDF
    # ============================================================

    doc.build(story)

if __name__ == "__main__":

    build_tearsheet("TCS")
