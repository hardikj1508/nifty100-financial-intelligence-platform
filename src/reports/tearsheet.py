import pandas as pd
from pathlib import Path

from reportlab.lib import colors
from reportlab.graphics.shapes import (
    Drawing,
    Rect,
    String,
    Line,
)
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics import renderPDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.enums import (
    TA_LEFT,
    TA_CENTER,
    TA_RIGHT,
)
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "output"

OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "tearsheet_template.pdf"

FINANCIAL_RATIO_FILE = DATA_DIR / "financial_ratios_clean.csv"
PROFIT_LOSS_FILE = DATA_DIR / "profitandloss_clean.csv"
COMPANIES_FILE = DATA_DIR / "companies_clean.csv"
BALANCE_SHEET_FILE = DATA_DIR / "balancesheet_clean.csv"
CASH_FLOW_FILE = DATA_DIR / "cashflow_clean.csv"


# ============================================================
# PAGE SETTINGS
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4

MARGIN_LEFT = 35
MARGIN_RIGHT = 35
MARGIN_TOP = 35
MARGIN_BOTTOM = 35


# ============================================================
# COLORS
# ============================================================

NAVY = colors.HexColor("#172554")
LIGHT_BLUE = colors.HexColor("#EFF6FF")
LIGHT_GREY = colors.HexColor("#F3F4F6")
DARK_GREY = colors.HexColor("#374151")

GREEN = colors.HexColor("#15803D")
LIGHT_GREEN = colors.HexColor("#DCFCE7")

RED = colors.HexColor("#B91C1C")
LIGHT_RED = colors.HexColor("#FEE2E2")

WHITE = colors.white


# ============================================================
# STYLES
# ============================================================

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
    fontName="Helvetica",
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
    alignment=TA_CENTER,
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


# ============================================================
# GENERAL HELPERS
# ============================================================

def safe_float(value):
    """
    Safely convert a value to float.

    Returns None for:
    - NaN
    - None
    - empty strings
    - non-numeric values
    """

    try:
        if value is None:
            return None

        if pd.isna(value):
            return None

        if isinstance(value, str):
            value = value.strip()

            if value == "":
                return None

            value = value.replace(",", "")
            value = value.replace("%", "")

        return float(value)

    except (ValueError, TypeError):
        return None


def add_placeholder(
    drawing,
    text,
    x=None,
    y=None,
    font_size=10,
):
    """
    Safely add a placeholder message to a ReportLab drawing.
    """

    if x is None:
        x = drawing.width / 2

    if y is None:
        y = drawing.height / 2

    drawing.add(
        String(
            x,
            y,
            str(text),
            fontName="Helvetica",
            fontSize=font_size,
            fillColor=NAVY,
            textAnchor="middle",
        )
    )

    return drawing


def clean_numeric_series(series):
    """
    Convert a pandas Series into numeric values safely.
    """

    return pd.to_numeric(
        series,
        errors="coerce",
    )


# ============================================================
# HEADER
# ============================================================

def create_header(company_name, ticker):

    header_data = [
        [
            Paragraph(
                str(company_name),
                company_styles,
            ),
            Paragraph(
                str(ticker),
                ticker_style,
            ),
        ]
    ]

    header = Table(
        header_data,
        colWidths=[
            PAGE_WIDTH - 160,
            90,
        ],
        rowHeights=[45],
    )

    header.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    NAVY,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "ALIGN",
                    (1, 0),
                    (1, 0),
                    "RIGHT",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
            ]
        )
    )

    return header


# ============================================================
# KPI TILES
# ============================================================

def create_kpi_tiles(data):

    revenue = safe_float(data.get("revenue"))
    net_profit = safe_float(data.get("net_profit"))
    net_margin = safe_float(data.get("net_margin"))
    roe = safe_float(data.get("roe"))
    roce = safe_float(data.get("roce"))
    debt_to_equity = safe_float(
        data.get("debt_to_equity")
    )

    kpis = [
        (
            "Revenue",
            f"₹{revenue:,.0f}"
            if revenue is not None
            else "N/A",
        ),
        (
            "Net Profit",
            f"₹{net_profit:,.0f}"
            if net_profit is not None
            else "N/A",
        ),
        (
            "Net Margin",
            f"{net_margin:.2f}%"
            if net_margin is not None
            else "N/A",
        ),
        (
            "ROE",
            f"{roe:.2f}%"
            if roe is not None
            else "N/A",
        ),
        (
            "ROCE",
            f"{roce:.2f}%"
            if roce is not None
            else "N/A",
        ),
        (
            "Debt / Equity",
            f"{debt_to_equity:.2f}"
            if debt_to_equity is not None
            else "N/A",
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
                        ),
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
                        ),
                    )
                ],
            ],
            colWidths=155,
            rowHeights=[18, 27],
        )

        cell.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        LIGHT_BLUE,
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

        cells.append(cell)

    kpi_table = Table(
        [
            cells[0:3],
            cells[3:6],
        ],
        colWidths=[
            170,
            170,
            170,
        ],
        rowHeights=[
            52,
            52,
        ],
        hAlign="CENTER",
    )

    kpi_table.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    3,
                ),
            ]
        )
    )

    return kpi_table


# ============================================================
# GENERIC CHART PLACEHOLDER
# ============================================================

def chart_placeholder(title, height=150):

    content = Table(
        [
            [
                Paragraph(
                    f"{title}<br/><br/>"
                    "Chart will be added in Phase 2",
                    placeholder_style,
                )
            ]
        ],
        colWidths=[250],
        rowHeights=[height],
    )

    content.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT_GREY,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.HexColor("#9CA3AF"),
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
            ]
        )
    )

    return content


# ============================================================
# BULLET SECTION
# ============================================================

def bullet_section(
    title,
    bullets,
    background,
    title_color,
):

    rows = [
        [
            Paragraph(
                title,
                ParagraphStyle(
                    "BulletTitle",
                    parent=styles["Normal"],
                    fontName="Helvetica-Bold",
                    textColor=title_color,
                ),
            )
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
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    background,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    title_color,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    return table


# ============================================================
# CAPITAL ALLOCATION
# ============================================================

def capital_allocation_badge(data):
    """
    Create a dynamic capital allocation assessment.
    """

    financial = data.get(
        "financial_history",
        pd.DataFrame(),
    )

    if financial is None:
        financial = pd.DataFrame()

    financial = financial.copy()

    if not financial.empty and "year" in financial.columns:
        financial = financial.sort_values("year")

    if financial.empty:
        latest = {}

    else:
        latest = financial.iloc[-1]

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

    # --------------------------------------------------------
    # DEBT / EQUITY
    # --------------------------------------------------------

    if debt_equity is not None:

        total += 1

        if debt_equity < 0.5:
            score += 1

    # --------------------------------------------------------
    # ROE
    # --------------------------------------------------------

    if roe is not None:

        total += 1

        if roe >= 15:
            score += 1

    # --------------------------------------------------------
    # DIVIDEND PAYOUT
    # --------------------------------------------------------

    if dividend_payout is not None:

        total += 1

        if 20 <= dividend_payout <= 70:
            score += 1

    # --------------------------------------------------------
    # FREE CASH FLOW
    # --------------------------------------------------------

    if free_cash_flow is not None:

        total += 1

        if free_cash_flow > 0:
            score += 1

    # --------------------------------------------------------
    # OVERALL ASSESSMENT
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # BADGE STYLES
    # --------------------------------------------------------

    badge_label_style = ParagraphStyle(
        "CapitalLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=NAVY,
        alignment=TA_CENTER,
    )

    badge_value_style = ParagraphStyle(
        "CapitalValue",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        textColor=colors.white,
        alignment=TA_CENTER,
    )

    badge = Table(
        [
            [
                Paragraph(
                    "CAPITAL ALLOCATION",
                    badge_label_style,
                )
            ],
            [
                Paragraph(
                    assessment,
                    badge_value_style,
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

    # --------------------------------------------------------
    # SUPPORTING METRICS
    # --------------------------------------------------------

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
                ),
            )
        )

    if not metric_paragraphs:

        metric_paragraphs.append(
            Paragraph(
                "• Supporting financial data not available",
                ParagraphStyle(
                    "CapitalMetricNA",
                    parent=styles["Normal"],
                    fontName="Helvetica",
                    fontSize=7.5,
                    leading=10,
                    textColor=DARK_GREY,
                ),
            )
        )

    metric_table = Table(
        [
            [metric]
            for metric in metric_paragraphs
        ],
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
        [
            [
                badge,
                metric_table,
            ]
        ],
        colWidths=[200, 200],
    )


# ============================================================
# LOAD COMPANY DATA
# ============================================================

def load_company_data(company_id):

    financial = pd.read_csv(
        FINANCIAL_RATIO_FILE
    )

    balance_sheet = pd.read_csv(
        BALANCE_SHEET_FILE
    )

    profit_loss = pd.read_csv(
        PROFIT_LOSS_FILE
    )

    companies = pd.read_csv(
        COMPANIES_FILE
    )

    cash_flow = pd.read_csv(
        CASH_FLOW_FILE
    )

    # --------------------------------------------------------
    # FILTER COMPANY DATA
    # --------------------------------------------------------

    financial = financial[
        financial["company_id"] == company_id
    ].copy()

    balance_sheet = balance_sheet[
        balance_sheet["company_id"] == company_id
    ].copy()

    profit_loss = profit_loss[
        profit_loss["company_id"] == company_id
    ].copy()

    cash_flow = cash_flow[
        cash_flow["company_id"] == company_id
    ].copy()

    # --------------------------------------------------------
    # SORT HISTORICAL DATA
    # --------------------------------------------------------

    if not financial.empty and "year" in financial.columns:
        financial = financial.sort_values("year")

    if not balance_sheet.empty and "year" in balance_sheet.columns:
        balance_sheet = balance_sheet.sort_values("year")

    if not profit_loss.empty and "year" in profit_loss.columns:
        profit_loss = profit_loss.sort_values("year")

    if not cash_flow.empty and "year" in cash_flow.columns:
        cash_flow = cash_flow.sort_values("year")

    # --------------------------------------------------------
    # PROFIT & LOSS IS REQUIRED
    # --------------------------------------------------------

    if profit_loss.empty:

        raise ValueError(
            f"No profit & loss data found for {company_id}"
        )

    latest_profit_loss = profit_loss.iloc[-1]

    # --------------------------------------------------------
    # COMPANY INFORMATION
    # --------------------------------------------------------

    company = companies[
        companies["id"] == company_id
    ].copy()

    if (
        company.empty
        and "company_id" in companies.columns
    ):

        company = companies[
            companies["company_id"] == company_id
        ].copy()

    if company.empty:

        raise ValueError(
            f"No company information found for {company_id}"
        )

    latest_company = company.iloc[-1]

    # --------------------------------------------------------
    # FINANCIAL-RATIO DATA
    # --------------------------------------------------------

    if financial.empty:

        latest_financial = None

        financial_history = pd.DataFrame(
            columns=[
                "company_id",
                "year",
                "return_on_equity_pct",
                "net_profit_margin_pct",
                "debt_to_equity",
                "equity_capital",
                "reserves",
                "borrowings",
                "other_liabilities",
            ]
        )

    else:

        latest_financial = financial.iloc[-1]

        # ----------------------------------------------------
        # MERGE FINANCIAL RATIOS WITH BALANCE SHEET
        # ----------------------------------------------------

        balance_columns = [
            "company_id",
            "year",
            "equity_capital",
            "reserves",
            "borrowings",
            "other_liabilities",
        ]

        available_balance_columns = [
            column
            for column in balance_columns
            if column in balance_sheet.columns
        ]

        if (
            "company_id" in available_balance_columns
            and "year" in available_balance_columns
        ):

            financial_history = financial.merge(
                balance_sheet[
                    available_balance_columns
                ],
                on=[
                    "company_id",
                    "year",
                ],
                how="left",
            )

        else:

            financial_history = financial.copy()

    # --------------------------------------------------------
    # SAFE KPI EXTRACTION
    # --------------------------------------------------------

    if latest_financial is None:

        net_margin = None
        roe = None
        debt_to_equity = None

    else:

        net_margin = safe_float(
            latest_financial.get(
                "net_profit_margin_pct"
            )
        )

        roe = safe_float(
            latest_financial.get(
                "return_on_equity_pct"
            )
        )

        debt_to_equity = safe_float(
            latest_financial.get(
                "debt_to_equity"
            )
        )

    # --------------------------------------------------------
    # ROCE
    # --------------------------------------------------------

    roce = safe_float(
        latest_company.get(
            "roce_percentage"
        )
    )

    # --------------------------------------------------------
    # REVENUE / NET PROFIT
    # --------------------------------------------------------

    revenue = safe_float(
        latest_profit_loss.get("sales")
    )

    net_profit = safe_float(
        latest_profit_loss.get("net_profit")
    )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return {
        "company_id": company_id,

        "company_name": latest_company.get(
            "company_name",
            company_id,
        ),

        "ticker": company_id,

        "revenue": revenue,

        "net_profit": net_profit,

        "net_margin": net_margin,

        "roe": roe,

        "roce": roce,

        "debt_to_equity": debt_to_equity,

        "profit_loss_history": profit_loss,

        "financial_history": financial_history,

        "cash_flow_history": cash_flow,
    }


# ============================================================
# FINANCIAL BAR CHART
# ============================================================

def create_financial_bar_chart(
    history,
    column,
    title,
):
    """
    Create a safe vertical bar chart.

    Handles:
    - empty DataFrames
    - missing columns
    - NaN values
    - non-numeric values
    - empty filtered series
    """

    drawing = Drawing(
        250,
        190,
    )

    # --------------------------------------------------------
    # DATAFRAME CHECK
    # --------------------------------------------------------

    if history is None or history.empty:

        return add_placeholder(
            drawing,
            f"{title} data not available",
        )

    # --------------------------------------------------------
    # COLUMN CHECK
    # --------------------------------------------------------

    if column not in history.columns:

        return add_placeholder(
            drawing,
            f"{title} data not available",
        )

    # --------------------------------------------------------
    # YEAR CHECK
    # --------------------------------------------------------

    if "year" not in history.columns:

        return add_placeholder(
            drawing,
            f"{title} data not available",
        )

    history = history.copy()

    # --------------------------------------------------------
    # NUMERIC CONVERSION
    # --------------------------------------------------------

    history[column] = pd.to_numeric(
        history[column],
        errors="coerce",
    )

    history = history.dropna(
        subset=[column]
    )

    if history.empty:

        return add_placeholder(
            drawing,
            f"{title} data not available",
        )

    # --------------------------------------------------------
    # LAST 10 PERIODS
    # --------------------------------------------------------

    history = (
        history
        .sort_values("year")
        .tail(10)
    )

    if history.empty:

        return add_placeholder(
            drawing,
            f"{title} data not available",
        )

    # --------------------------------------------------------
    # VALUES
    # --------------------------------------------------------

    labels = (
        history["year"]
        .astype(str)
        .tolist()
    )

    values = [
        safe_float(value)
        for value in history[column].tolist()
    ]

    clean_pairs = [
        (label, value)
        for label, value in zip(
            labels,
            values,
        )
        if value is not None
    ]

    if not clean_pairs:

        return add_placeholder(
            drawing,
            f"{title} data not available",
        )

    labels = [
        pair[0]
        for pair in clean_pairs
    ]

    values = [
        pair[1]
        for pair in clean_pairs
    ]

    if not values:

        return add_placeholder(
            drawing,
            f"{title} data not available",
        )

    # --------------------------------------------------------
    # CHART
    # --------------------------------------------------------

    chart = VerticalBarChart()

    chart.x = 35
    chart.y = 35

    chart.width = 205
    chart.height = 125

    # ReportLab requires a non-empty nested sequence.
    chart.data = [values]

    chart.categoryAxis.categoryNames = labels

    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 7

    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 7

    # --------------------------------------------------------
    # VALUE RANGE
    # --------------------------------------------------------

    minimum_value = min(values)
    maximum_value = max(values)

    if minimum_value == maximum_value:

        if minimum_value == 0:

            chart.valueAxis.valueMin = -1
            chart.valueAxis.valueMax = 1

        else:

            padding = abs(minimum_value) * 0.20

            if padding == 0:
                padding = 1

            chart.valueAxis.valueMin = (
                minimum_value - padding
            )

            chart.valueAxis.valueMax = (
                maximum_value + padding
            )

    else:

        padding = (
            maximum_value - minimum_value
        ) * 0.10

        if minimum_value >= 0:

            chart.valueAxis.valueMin = 0

        else:

            chart.valueAxis.valueMin = (
                minimum_value - padding
            )

        chart.valueAxis.valueMax = (
            maximum_value + padding
        )

    # --------------------------------------------------------
    # APPEARANCE
    # --------------------------------------------------------

    chart.barWidth = 12
    chart.groupSpacing = 10

    chart.strokeColor = colors.HexColor(
        "#CBD5E1"
    )

    chart.valueAxis.strokeColor = colors.HexColor(
        "#94A3B8"
    )

    chart.categoryAxis.strokeColor = colors.HexColor(
        "#94A3B8"
    )

    drawing.add(chart)

    return drawing


# ============================================================
# ROE CHART
# ============================================================

def create_roe_chart(history):
    """
    Create a historical ROE line chart safely.
    """

    drawing = Drawing(
        470,
        190,
    )

    if history is None or history.empty:

        return add_placeholder(
            drawing,
            "ROE data not available",
        )

    if "year" not in history.columns:

        return add_placeholder(
            drawing,
            "ROE data not available",
        )

    if "return_on_equity_pct" not in history.columns:

        return add_placeholder(
            drawing,
            "ROE data not available",
        )

    history = history.copy()

    history["return_on_equity_pct"] = pd.to_numeric(
        history["return_on_equity_pct"],
        errors="coerce",
    )

    history = history.dropna(
        subset=["return_on_equity_pct"]
    )

    if history.empty:

        return add_placeholder(
            drawing,
            "ROE data not available",
        )

    history = (
        history
        .sort_values("year")
        .tail(10)
    )

    labels = (
        history["year"]
        .astype(str)
        .tolist()
    )

    values = (
        history[
            "return_on_equity_pct"
        ]
        .tolist()
    )

    if not values:

        return add_placeholder(
            drawing,
            "ROE data not available",
        )

    chart = HorizontalLineChart()

    chart.x = 45
    chart.y = 35

    chart.width = 400
    chart.height = 125

    chart.data = [values]

    chart.categoryAxis.categoryNames = labels

    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 7

    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 7

    minimum = min(values)
    maximum = max(values)

    if minimum == maximum:

        padding = (
            10
            if minimum == 0
            else abs(minimum) * 0.20
        )

    else:

        padding = (
            maximum - minimum
        ) * 0.10

    chart.valueAxis.valueMin = (
        minimum - padding
    )

    chart.valueAxis.valueMax = (
        maximum + padding
    )

    chart.lines[0].strokeWidth = 2

    drawing.add(chart)

    return drawing


# ============================================================
# BALANCE SHEET CHART
# ============================================================

def create_balance_sheet_chart(history):
    """
    Safe balance-sheet composition chart.

    Handles:
    - completely missing financial history
    - individual missing columns
    - NaN values
    - empty chart series
    """

    drawing = Drawing(
        470,
        190,
    )

    # --------------------------------------------------------
    # BASIC CHECK
    # --------------------------------------------------------

    if history is None or history.empty:

        return add_placeholder(
            drawing,
            "Balance sheet data not available",
        )

    history = history.copy()

    if "year" not in history.columns:

        return add_placeholder(
            drawing,
            "Balance sheet data not available",
        )

    history = (
        history
        .sort_values("year")
        .tail(10)
    )

    if history.empty:

        return add_placeholder(
            drawing,
            "Balance sheet data not available",
        )

    # --------------------------------------------------------
    # REQUIRED SERIES
    # --------------------------------------------------------

    required_columns = [
        "equity_capital",
        "reserves",
        "borrowings",
        "other_liabilities",
    ]

    series = []

    for column in required_columns:

        if column in history.columns:

            values = (
                pd.to_numeric(
                    history[column],
                    errors="coerce",
                )
                .fillna(0)
                .tolist()
            )

        else:

            values = [
                0
            ] * len(history)

        series.append(values)

    # --------------------------------------------------------
    # SERIES CHECK
    # --------------------------------------------------------

    if not series:

        return add_placeholder(
            drawing,
            "Balance sheet data not available",
        )

    if len(series[0]) == 0:

        return add_placeholder(
            drawing,
            "Balance sheet data not available",
        )

    # --------------------------------------------------------
    # REAL DATA CHECK
    # --------------------------------------------------------

    has_real_data = any(
        value != 0
        for values in series
        for value in values
    )

    if not has_real_data:

        return add_placeholder(
            drawing,
            "Balance sheet data not available",
        )

    # --------------------------------------------------------
    # YEARS
    # --------------------------------------------------------

    years = (
        history["year"]
        .astype(str)
        .tolist()
    )

    if not years:

        return add_placeholder(
            drawing,
            "Balance sheet data not available",
        )

    # --------------------------------------------------------
    # CHART
    # --------------------------------------------------------

    chart = VerticalBarChart()

    chart.x = 45
    chart.y = 45

    chart.width = 400
    chart.height = 125

    chart.data = series

    chart.categoryAxis.categoryNames = years

    chart.categoryAxis.labels.fontName = "Helvetica"
    chart.categoryAxis.labels.fontSize = 7

    chart.valueAxis.labels.fontName = "Helvetica"
    chart.valueAxis.labels.fontSize = 7

    chart.valueAxis.valueMin = 0

    chart.barWidth = 18
    chart.groupSpacing = 10

    chart.strokeColor = colors.HexColor(
        "#CBD5E1"
    )

    chart.valueAxis.strokeColor = colors.HexColor(
        "#94A3B8"
    )

    chart.categoryAxis.strokeColor = colors.HexColor(
        "#94A3B8"
    )

    # --------------------------------------------------------
    # BAR COLORS
    # --------------------------------------------------------

    chart.bars[0].fillColor = NAVY

    chart.bars[1].fillColor = colors.HexColor(
        "#5B8FF9"
    )

    chart.bars[2].fillColor = colors.HexColor(
        "#F5A623"
    )

    chart.bars[3].fillColor = colors.HexColor(
        "#7CB342"
    )

    drawing.add(chart)

    return drawing


# ============================================================
# CASH FLOW WATERFALL
# ============================================================

def create_cash_flow_waterfall(history):
    """
    Create a cash-flow waterfall for the latest year.

    Shows:
    CFO -> CFI -> CFF -> Net Cash Flow
    """

    width = 470
    height = 160

    drawing = Drawing(
        width,
        height,
    )

    # --------------------------------------------------------
    # BASIC CHECK
    # --------------------------------------------------------

    if history is None or history.empty:

        return add_placeholder(
            drawing,
            "Cash flow data not available",
            235,
            80,
        )

    history = history.copy()

    if "year" in history.columns:

        history = history.sort_values(
            "year"
        )

    latest = history.iloc[-1]

    # --------------------------------------------------------
    # SAFE VALUES
    # --------------------------------------------------------

    cfo = safe_float(
        latest.get("operating_activity")
    )

    cfi = safe_float(
        latest.get("investing_activity")
    )

    cff = safe_float(
        latest.get("financing_activity")
    )

    net_cash = safe_float(
        latest.get("net_cash_flow")
    )

    if any(
        value is None
        for value in [
            cfo,
            cfi,
            cff,
            net_cash,
        ]
    ):

        return add_placeholder(
            drawing,
            "Cash flow data not available",
            235,
            80,
        )

    # --------------------------------------------------------
    # RUNNING TOTALS
    # --------------------------------------------------------

    start_cfo = 0
    end_cfo = cfo

    start_cfi = end_cfo
    end_cfi = end_cfo + cfi

    start_cff = end_cfi
    end_cff = end_cfi + cff

    # --------------------------------------------------------
    # DIMENSIONS
    # --------------------------------------------------------

    left = 45
    bottom = 35
    chart_width = 390
    chart_height = 100

    # --------------------------------------------------------
    # SCALE
    # --------------------------------------------------------

    all_values = [
        0,
        end_cfo,
        end_cfi,
        end_cff,
        net_cash,
    ]

    min_value = min(all_values)
    max_value = max(all_values)

    value_range = (
        max_value - min_value
    )

    padding = value_range * 0.15

    if padding == 0:
        padding = 1

    y_min = min_value - padding
    y_max = max_value + padding

    denominator = (
        y_max - y_min
    )

    if denominator == 0:
        denominator = 1

    def y(value):

        return bottom + (
            (
                value - y_min
            )
            / denominator
        ) * chart_height

    # --------------------------------------------------------
    # BASELINE
    # --------------------------------------------------------

    zero_y = y(0)

    drawing.add(
        Line(
            left,
            zero_y,
            left + chart_width,
            zero_y,
            strokeColor=colors.HexColor(
                "#777777"
            ),
            strokeWidth=0.7,
        )
    )

    # --------------------------------------------------------
    # BARS
    # --------------------------------------------------------

    labels = [
        "CFO",
        "CFI",
        "CFF",
        "Net Cash Flow",
    ]

    bar_values = [
        cfo,
        cfi,
        cff,
        net_cash,
    ]

    bar_bottoms = [
        start_cfo,
        start_cfi,
        start_cff,
        0,
    ]

    bar_tops = [
        end_cfo,
        end_cfi,
        end_cff,
        net_cash,
    ]

    bar_width = 55
    spacing = 40

    x_positions = [
        left + 25,
        left + 25
        + bar_width
        + spacing,
        left + 25
        + 2 * (
            bar_width + spacing
        ),
        left + 25
        + 3 * (
            bar_width + spacing
        ),
    ]

    # --------------------------------------------------------
    # DRAW BARS
    # --------------------------------------------------------

    for i in range(4):

        value = bar_values[i]

        bar_bottom = bar_bottoms[i]
        bar_top = bar_tops[i]

        y_bottom = y(
            min(
                bar_bottom,
                bar_top,
            )
        )

        y_top = y(
            max(
                bar_bottom,
                bar_top,
            )
        )

        bar_height = (
            y_top - y_bottom
        )

        if i == 3:

            fill = NAVY

        elif value >= 0:

            fill = colors.HexColor(
                "#7CB342"
            )

        else:

            fill = colors.HexColor(
                "#D9534F"
            )

        # Avoid zero-height visual issues.
        if bar_height < 0.5:
            bar_height = 0.5

        drawing.add(
            Rect(
                x_positions[i],
                y_bottom,
                bar_width,
                bar_height,
                fillColor=fill,
                strokeColor=colors.HexColor(
                    "#333333"
                ),
                strokeWidth=0.6,
            )
        )

        # ----------------------------------------------------
        # VALUE LABEL
        # ----------------------------------------------------

        label_y = y_top + 5

        if value < 0:
            label_y = y_bottom - 13

        drawing.add(
            String(
                x_positions[i]
                + bar_width / 2,
                label_y,
                f"{value:,.0f}",
                fontName="Helvetica-Bold",
                fontSize=7,
                textAnchor="middle",
            )
        )

        # ----------------------------------------------------
        # CATEGORY LABEL
        # ----------------------------------------------------

        drawing.add(
            String(
                x_positions[i]
                + bar_width / 2,
                bottom - 15,
                labels[i],
                fontName="Helvetica-Bold",
                fontSize=7,
                textAnchor="middle",
                fillColor=colors.HexColor(
                    "#222222"
                ),
            )
        )

    # --------------------------------------------------------
    # CONNECTOR LINES
    # --------------------------------------------------------

    connector_color = colors.HexColor(
        "#888888"
    )

    # CFO -> CFI
    drawing.add(
        Line(
            x_positions[0] + bar_width,
            y(end_cfo),
            x_positions[1],
            y(end_cfo),
            strokeColor=connector_color,
            strokeWidth=0.6,
        )
    )

    # CFI -> CFF
    drawing.add(
        Line(
            x_positions[1] + bar_width,
            y(end_cfi),
            x_positions[2],
            y(end_cfi),
            strokeColor=connector_color,
            strokeWidth=0.6,
        )
    )

    # CFF -> Net Cash Flow
    drawing.add(
        Line(
            x_positions[2] + bar_width,
            y(end_cff),
            x_positions[3],
            y(net_cash),
            strokeColor=connector_color,
            strokeWidth=0.6,
        )
    )

    return drawing


# ============================================================
# PROS / CONS
# ============================================================

def create_pros_cons_section(data):
    """
    Generate a dynamic Investment View based on
    latest financial and cash-flow data.
    """

    financial = data.get(
        "financial_history",
        pd.DataFrame(),
    )

    if financial is None:
        financial = pd.DataFrame()

    financial = financial.copy()

    if not financial.empty and "year" in financial.columns:

        financial = financial.sort_values(
            "year"
        )

    if financial.empty:

        latest = {}

    else:

        latest = financial.iloc[-1]

    cash_flow = data.get(
        "cash_flow_history"
    )

    pros = []
    cons = []

    # --------------------------------------------------------
    # LATEST FINANCIAL METRICS
    # --------------------------------------------------------

    roe = safe_float(
        latest.get(
            "return_on_equity_pct"
        )
    )

    debt_equity = safe_float(
        latest.get(
            "debt_to_equity"
        )
    )

    net_margin = safe_float(
        latest.get(
            "net_profit_margin_pct"
        )
    )

    operating_margin = safe_float(
        latest.get(
            "operating_profit_margin_pct"
        )
    )

    # --------------------------------------------------------
    # PROFITABILITY
    # --------------------------------------------------------

    if roe is not None:

        if roe >= 20:

            pros.append(
                f"Strong ROE of {roe:.1f}%"
            )

        elif roe >= 15:

            pros.append(
                f"Healthy ROE of {roe:.1f}%"
            )

        elif roe < 10:

            cons.append(
                f"Low ROE of {roe:.1f}%"
            )

    if net_margin is not None:

        if net_margin >= 15:

            pros.append(
                f"Strong net margin of "
                f"{net_margin:.1f}%"
            )

        elif net_margin < 10:

            cons.append(
                f"Low net margin of "
                f"{net_margin:.1f}%"
            )

    if operating_margin is not None:

        if operating_margin >= 15:

            pros.append(
                f"Healthy operating margin "
                f"of {operating_margin:.1f}%"
            )

        elif operating_margin < 10:

            cons.append(
                f"Low operating margin "
                f"of {operating_margin:.1f}%"
            )

    # --------------------------------------------------------
    # DEBT
    # --------------------------------------------------------

    if debt_equity is not None:

        if debt_equity < 0.5:

            pros.append(
                "Low financial leverage "
                f"(Debt/Equity {debt_equity:.2f}x)"
            )

        elif debt_equity > 1:

            cons.append(
                "High financial leverage "
                f"(Debt/Equity {debt_equity:.2f}x)"
            )

    # --------------------------------------------------------
    # CASH FLOW
    # --------------------------------------------------------

    if (
        cash_flow is not None
        and not cash_flow.empty
    ):

        cash_flow = cash_flow.copy()

        if "year" in cash_flow.columns:

            cash_flow = cash_flow.sort_values(
                "year"
            )

        latest_cf = cash_flow.iloc[-1]

        cfo = safe_float(
            latest_cf.get(
                "operating_activity"
            )
        )

        cfi = safe_float(
            latest_cf.get(
                "investing_activity"
            )
        )

        cff = safe_float(
            latest_cf.get(
                "financing_activity"
            )
        )

        net_cash = safe_float(
            latest_cf.get(
                "net_cash_flow"
            )
        )

        if cfo is not None:

            if cfo > 0:

                pros.append(
                    f"Positive operating cash flow "
                    f"of {cfo:,.0f}"
                )

            elif cfo < 0:

                cons.append(
                    "Negative operating cash flow"
                )

        if cfi is not None and cfi < 0:

            pros.append(
                "Investment outflow indicates "
                "continued capital deployment"
            )

        if cff is not None and cff < 0:

            cons.append(
                "Negative financing cash flow"
            )

        if net_cash is not None:

            if net_cash > 0:

                pros.append(
                    f"Positive net cash flow "
                    f"of {net_cash:,.0f}"
                )

            elif net_cash < 0:

                cons.append(
                    "Negative net cash flow"
                )

    # --------------------------------------------------------
    # REVENUE / PROFIT TREND
    # --------------------------------------------------------

    profit_loss = data.get(
        "profit_loss_history"
    )

    if (
        profit_loss is not None
        and not profit_loss.empty
    ):

        profit_loss = profit_loss.copy()

        if "year" in profit_loss.columns:

            profit_loss = profit_loss.sort_values(
                "year"
            )

        if len(profit_loss) >= 2:

            first = profit_loss.iloc[0]
            last = profit_loss.iloc[-1]

            first_sales = safe_float(
                first.get("sales")
            )

            last_sales = safe_float(
                last.get("sales")
            )

            first_profit = safe_float(
                first.get("net_profit")
            )

            last_profit = safe_float(
                last.get("net_profit")
            )

            if (
                first_sales is not None
                and last_sales is not None
                and last_sales > first_sales
            ):

                pros.append(
                    "Long-term revenue growth"
                )

            if (
                first_profit is not None
                and last_profit is not None
                and last_profit > first_profit
            ):

                pros.append(
                    "Long-term net profit growth"
                )

    # --------------------------------------------------------
    # LIMIT ITEMS
    # --------------------------------------------------------

    pros = pros[:5]
    cons = cons[:5]

    # --------------------------------------------------------
    # FALLBACKS
    # --------------------------------------------------------

    if not pros:

        pros.append(
            "No major positive indicator identified"
        )

    if not cons:

        cons.append(
            "No major negative indicator identified"
        )

    # --------------------------------------------------------
    # STYLES
    # --------------------------------------------------------

    investment_bullet_style = ParagraphStyle(
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
        textColor=colors.HexColor(
            "#2E7D32"
        ),
    )

    header_style_con = ParagraphStyle(
        "ConsHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=colors.HexColor(
            "#D32F2F"
        ),
    )

    # --------------------------------------------------------
    # PROS
    # --------------------------------------------------------

    pros_content = [
        [
            Paragraph(
                "Pros",
                header_style_pro,
            )
        ]
    ]

    for item in pros:

        pros_content.append(
            [
                Paragraph(
                    f"• {item}",
                    investment_bullet_style,
                )
            ]
        )

    # --------------------------------------------------------
    # CONS
    # --------------------------------------------------------

    cons_content = [
        [
            Paragraph(
                "Cons",
                header_style_con,
            )
        ]
    ]

    for item in cons:

        cons_content.append(
            [
                Paragraph(
                    f"• {item}",
                    investment_bullet_style,
                )
            ]
        )

    # --------------------------------------------------------
    # PROS TABLE
    # --------------------------------------------------------

    pros_table = Table(
        pros_content,
        colWidths=[190],
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

    # --------------------------------------------------------
    # CONS TABLE
    # --------------------------------------------------------

    cons_table = Table(
        cons_content,
        colWidths=[190],
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

    # --------------------------------------------------------
    # SIDE-BY-SIDE
    # --------------------------------------------------------

    investment_view = Table(
        [
            [
                pros_table,
                cons_table,
            ]
        ],
        colWidths=[
            195,
            195,
        ],
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
            section_style,
        ),
        Spacer(1, 8),
        investment_view,
    ]


# ============================================================
# PEER COMPARISON
# ============================================================

def create_peer_comparision_section(data):
    """
    Create a peer comparison table.

    This function remains available but is not called by the
    current build_tearsheet() flow.
    """

    peer_file = (
        PROJECT_ROOT
        / "reports"
        / "peer_comparison.xlsx"
    )

    if not peer_file.exists():

        return [
            Paragraph(
                "Peer Comparison",
                section_style,
            ),
            Spacer(1, 8),
            Paragraph(
                "Peer comparison data not available.",
                placeholder_style,
            ),
        ]

    try:

        df = pd.read_excel(
            peer_file,
            sheet_name="IT Services",
        )

    except Exception:

        return [
            Paragraph(
                "Peer Comparison",
                section_style,
            ),
            Spacer(1, 8),
            Paragraph(
                "Peer comparison data not available.",
                placeholder_style,
            ),
        ]

    if df.empty:

        return [
            Paragraph(
                "Peer Comparison",
                section_style,
            ),
            Spacer(1, 8),
            Paragraph(
                "Peer comparison data not available.",
                placeholder_style,
            ),
        ]

    if "year" not in df.columns:

        return [
            Paragraph(
                "Peer Comparison",
                section_style,
            ),
            Spacer(1, 8),
            Paragraph(
                "Peer comparison year data not available.",
                placeholder_style,
            ),
        ]

    latest_year = df["year"].max()

    peers = df[
        df["year"] == latest_year
    ].copy()

    columns = [
        "company_name",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "return_on_equity_pct",
        "debt_to_equity",
        "free_cash_flow_cr",
    ]

    available_columns = [
        column
        for column in columns
        if column in peers.columns
    ]

    if "company_name" not in available_columns:

        return [
            Paragraph(
                "Peer Comparison",
                section_style,
            ),
            Spacer(1, 8),
            Paragraph(
                "Peer comparison data not available.",
                placeholder_style,
            ),
        ]

    peers = peers[
        available_columns
    ].copy()

    peers["is_tcs"] = peers[
        "company_name"
    ].eq(
        "Tata Consultancy Services Ltd"
    )

    sort_columns = ["is_tcs"]

    ascending = [False]

    if "return_on_equity_pct" in peers.columns:

        sort_columns.append(
            "return_on_equity_pct"
        )

        ascending.append(False)

    peers = peers.sort_values(
        sort_columns,
        ascending=ascending,
    )

    peers = peers.drop(
        columns=["is_tcs"]
    )

    elements = [
        Paragraph(
            "Peer Comparison",
            section_style,
        ),
        Spacer(1, 12),
    ]

    table_data = [
        [
            "Company",
            "Net Margin",
            "Operating Margin",
            "ROE",
            "Debt / Equity",
            "Free Cash Flow",
        ]
    ]

    for _, row in peers.iterrows():

        net_margin = safe_float(
            row.get(
                "net_profit_margin_pct"
            )
        )

        op_margin = safe_float(
            row.get(
                "operating_profit_margin_pct"
            )
        )

        roe = safe_float(
            row.get(
                "return_on_equity_pct"
            )
        )

        de = safe_float(
            row.get(
                "debt_to_equity"
            )
        )

        fcf = safe_float(
            row.get(
                "free_cash_flow_cr"
            )
        )

        table_data.append(
            [
                str(
                    row.get(
                        "company_name",
                        "N/A",
                    )
                ),
                (
                    f"{net_margin:.2f}%"
                    if net_margin is not None
                    else "N/A"
                ),
                (
                    f"{op_margin:.2f}%"
                    if op_margin is not None
                    else "N/A"
                ),
                (
                    f"{roe:.2f}%"
                    if roe is not None
                    else "N/A"
                ),
                (
                    f"{de:.2f}x"
                    if de is not None
                    else "N/A"
                ),
                (
                    f"{fcf:,.0f}"
                    if fcf is not None
                    else "N/A"
                ),
            ]
        )

    table = Table(
        table_data,
        colWidths=[
            155,
            60,
            85,
            55,
            70,
            80,
        ],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    NAVY,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, 0),
                    7,
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (-1, -1),
                    "CENTER",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#CBD5E1"
                    ),
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor(
                            "#F7F9FC"
                        ),
                    ],
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
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

    elements.append(table)
    elements.append(Spacer(1, 12))

    return elements


# ============================================================
# BUILD TEARSHEET
# ============================================================

def build_tearsheet(company_id="TCS"):

    # ========================================================
    # LOAD DATA
    # ========================================================

    data = load_company_data(
        company_id
    )

    company_name = data[
        "company_name"
    ]

    ticker = data[
        "ticker"
    ]

    # ========================================================
    # OUTPUT
    # ========================================================

    output_file = (
        OUTPUT_DIR
        / f"{company_id}_tearsheet.pdf"
    )

    # ========================================================
    # DOCUMENT
    # ========================================================

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        leftMargin=MARGIN_LEFT,
        rightMargin=MARGIN_RIGHT,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
    )

    story = []

    # ========================================================
    # PAGE 1
    # ========================================================

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    story.append(
        Table(
            [
                [
                    Paragraph(
                        str(company_name),
                        ParagraphStyle(
                            "BuildCompanyName",
                            parent=styles["Normal"],
                            fontName="Helvetica-Bold",
                            fontSize=20,
                            textColor=colors.white,
                        ),
                    ),
                    Paragraph(
                        str(ticker),
                        ParagraphStyle(
                            "BuildTicker",
                            parent=styles["Normal"],
                            fontName="Helvetica",
                            fontSize=11,
                            textColor=colors.white,
                            alignment=TA_RIGHT,
                        ),
                    ),
                ]
            ],
            colWidths=[
                400,
                70,
            ],
            rowHeights=[60],
            style=TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        NAVY,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (0, 0),
                        18,
                    ),
                    (
                        "RIGHTPADDING",
                        (-1, 0),
                        (-1, 0),
                        18,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            ),
        )
    )

    story.append(
        Spacer(1, 12)
    )

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Key Performance Indicators",
            section_style,
        )
    )

    story.append(
        create_kpi_tiles(data)
    )

    story.append(
        Spacer(1, 12)
    )

    # --------------------------------------------------------
    # REVENUE & NET PROFIT
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Revenue & Net Profit - 10 Year Trend",
            section_style,
        )
    )

    history = data[
        "profit_loss_history"
    ].copy()

    revenue_chart = create_financial_bar_chart(
        history,
        "sales",
        "10-Year Revenue",
    )

    profit_chart = create_financial_bar_chart(
        history,
        "net_profit",
        "10-Year Net Profit",
    )

    revenue_profit = Table(
        [
            [
                revenue_chart,
                profit_chart,
            ]
        ],
        colWidths=[
            235,
            235,
        ],
        rowHeights=[190],
    )

    revenue_profit.setStyle(
        TableStyle(
            [
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    story.append(
        revenue_profit
    )

    story.append(
        Spacer(1, 8)
    )

    # --------------------------------------------------------
    # ROE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Return on Equity - Historical Trend",
            section_style,
        )
    )

    roe_chart = create_roe_chart(
        data[
            "financial_history"
        ]
    )

    story.append(
        roe_chart
    )

    story.append(
        Spacer(1, 8)
    )

    # ========================================================
    # PAGE 2
    # ========================================================

    story.append(
        PageBreak()
    )

    # --------------------------------------------------------
    # BALANCE SHEET
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Balance Sheet Composition",
            section_style,
        )
    )

    balance_sheet_chart = (
        create_balance_sheet_chart(
            data[
                "financial_history"
            ]
        )
    )

    story.append(
        balance_sheet_chart
    )

    story.append(
        Spacer(1, 8)
    )

    # --------------------------------------------------------
    # CASH FLOW
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Cash Flow - Latest Year",
            section_style,
        )
    )

    story.append(
        Spacer(1, 8)
    )

    cash_flow_waterfall = (
        create_cash_flow_waterfall(
            data[
                "cash_flow_history"
            ]
        )
    )

    story.append(
        cash_flow_waterfall
    )

    story.append(
        Spacer(1, 10)
    )

    # --------------------------------------------------------
    # INVESTMENT VIEW
    # --------------------------------------------------------

    story.extend(
        create_pros_cons_section(
            data
        )
    )

    story.append(
        Spacer(1, 10)
    )

    # --------------------------------------------------------
    # CAPITAL ALLOCATION
    # --------------------------------------------------------

    capital_allocation_section = KeepTogether(
        [
            Paragraph(
                "Capital Allocation",
                section_style,
            ),
            Spacer(1, 8),
            capital_allocation_badge(
                data
            ),
        ]
    )

    story.append(
        capital_allocation_section
    )

    # ========================================================
    # PEER COMPARISON
    #
    # Intentionally disabled in current 2-page tearsheet.
    # The existing peer file is specifically IT Services/TCS.
    # ========================================================

    # story.append(PageBreak())
    #
    # peer_section = create_peer_comparision_section(data)
    #
    # for element in peer_section:
    #     story.append(element)

    # ========================================================
    # BUILD PDF
    # ========================================================

    doc.build(
        story
    )

    return output_file


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    build_tearsheet(
        "TCS"
    )