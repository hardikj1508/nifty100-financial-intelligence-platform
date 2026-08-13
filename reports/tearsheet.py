import streamlit as st
from pathlib import path


from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getsampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)

OUTPUT_DIR = path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "tearsheet_ template.pdf"

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


styles = getsampleStyleSheet()

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

def create_kpi_tiles():

    kpis = [
        ("Revenue","₹--"),
        ("Net Profit","₹--"),
        ("Net Margin","--%"),
        ("ROE","--%"),
        ("ROCE","--%"),
        ("Debt / Equity","--"),
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
                            textColour=DARK_GREY,
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
                    ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
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
            cells[3:6]
        ],
        colWidths=[170,170,170],
        rowHeights=[52,52],
        hAlign="CENTER",
    )

    kpi_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0),(-1, -1), 3) 
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
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GREY)
                ("BOX", (0, 0),(-1, -1),0.7, colors.HexColor("#9CA3AF"),)
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
                    fontName="Helvetica_Bold",
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
        colWidths=[50],
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

