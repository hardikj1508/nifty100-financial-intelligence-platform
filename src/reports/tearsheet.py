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

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "tearsheet_ template.pdf"

FINANCIAL_RATIO_FILE = DATA_DIR / "financial_ratios_clean.csv"
PROFIT_LOSS_FILE = DATA_DIR / "profitandloss_clean.csv"
COMPANIES_FILE = DATA_DIR / "companies_clean.csv"
BALANCE_SHEET_FILE = DATA_DIR / "balancesheet_clean.csv"

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

def capital_allocation_badge():

    badge = Table(
        [
            [
                Paragraph(
                    "   CAPITAL ALLOCATION",
                    ParagraphStyle(
                        "BadgeTitle",
                        parent=styles["Normal"],
                        fontName="Helvetica-Bold",
                        fontSize=9,
                        textColor=WHITE,
                        alignment=TA_CENTER,
                    )
                )
            ],
            [
                Paragraph(
                    "REINVESTOR",
                    ParagraphStyle(
                        "BadgeValue",
                        parent=styles["Normal"],
                        fontName="Helvetica-Bold",
                        fontSize=14,
                        textColor=NAVY,
                        alignment=TA_CENTER,
                    ),
                )
            ],
        ],
        colWidths=[180],
        rowHeights=[25, 35],
    )

    badge.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("BACKGGROUND", (0, 1), (-1, 1), LIGHT_BLUE),
                ("BOX", (0, 0),  (-1, -1), 0.7, NAVY),
                ("VALIGN", (0, 0),(-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]    
        )
    )    
    return badge

def load_company_data(company_id):

    financial = pd.read_csv(FINANCIAL_RATIO_FILE)
    balance_sheet = pd.read_csv(BALANCE_SHEET_FILE)
    profit_loss = pd.read_csv(PROFIT_LOSS_FILE)
    companies = pd.read_csv(COMPANIES_FILE)

    financial = financial[
        financial["company_id"] == company_id
    ].copy()

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

    chart.barMode = "stacked"

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


