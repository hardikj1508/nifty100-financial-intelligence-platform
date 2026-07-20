"""
Rule definitions for Pros & Cons Generator.

Each rule contains:
- id
- description
- confidence score

The actual evaluation logic is implemented in
pros_cons_generator.py.
"""

# ==========================================================
# PRO RULES
# ==========================================================

PRO_RULES = [
    {
        "id": "P1",
        "name": "High ROE",
        "text": "Consistently high return on equity above 20% demonstrates exceptional capital efficiency.",
        "confidence": 95,
    },
    {
        "id": "P2",
        "name": "Strong Free Cash Flow",
        "text": "Strong free cash flow generation over five years signals healthy business fundamentals.",
        "confidence": 92,
    },
    {
        "id": "P3",
        "name": "Debt Free",
        "text": "Debt-free balance sheet provides financial flexibility and eliminates interest burden.",
        "confidence": 90,
    },
    {
        "id": "P4",
        "name": "Strong Revenue CAGR",
        "text": "Revenue growing above 15% CAGR over five years reflects strong business momentum.",
        "confidence": 90,
    },
    {
        "id": "P5",
        "name": "High Operating Margin",
        "text": "Operating profit margin above 25% indicates strong pricing power and cost discipline.",
        "confidence": 88,
    },
    {
        "id": "P6",
        "name": "Strong Profit CAGR",
        "text": "Net profit compounding above 20% over five years creates significant shareholder value.",
        "confidence": 90,
    },
    {
        "id": "P7",
        "name": "Excellent Interest Coverage",
        "text": "Very high interest coverage reflects negligible financial stress from debt servicing.",
        "confidence": 85,
    },
    {
        "id": "P8",
        "name": "Healthy Dividend Yield",
        "text": "Consistent dividend yield backed by positive free cash flow reflects healthy capital allocation.",
        "confidence": 82,
    },
    {
        "id": "P9",
        "name": "Strong EPS Growth",
        "text": "Strong earnings per share growth indicates improving shareholder returns.",
        "confidence": 85,
    },
    {
        "id": "P10",
        "name": "Improving ROE",
        "text": "Return on equity has improved consistently over recent years.",
        "confidence": 82,
    },
    {
        "id": "P11",
        "name": "Operating Leverage",
        "text": "Profit growth exceeding revenue growth indicates improving operating leverage.",
        "confidence": 80,
    },
    {
        "id": "P12",
        "name": "Balance Sheet Strength",
        "text": "Growing asset base while reducing debt reflects sustainable long-term growth.",
        "confidence": 85,
    },
]

# ==========================================================
# CON RULES
# ==========================================================

CON_RULES = [
    {
        "id": "C1",
        "name": "High Debt",
        "text": "Debt-to-equity ratio is elevated for a non-financial company and warrants monitoring.",
        "confidence": 90,
    },
    {
        "id": "C2",
        "name": "Negative Free Cash Flow",
        "text": "Negative free cash flow raises concern about cash generation quality.",
        "confidence": 92,
    },
    {
        "id": "C3",
        "name": "Declining Operating Margin",
        "text": "Operating margins have weakened over recent years.",
        "confidence": 88,
    },
    {
        "id": "C4",
        "name": "Net Loss",
        "text": "Company reported a net loss in the latest financial year.",
        "confidence": 95,
    },
    {
        "id": "C5",
        "name": "Revenue Decline",
        "text": "Revenue contraction indicates weakening business momentum.",
        "confidence": 85,
    },
    {
        "id": "C6",
        "name": "Weak Interest Coverage",
        "text": "Low interest coverage indicates risk in servicing debt obligations.",
        "confidence": 90,
    },
    {
        "id": "C7",
        "name": "Unsustainable Dividend",
        "text": "Dividend payout exceeds earnings and may not be sustainable.",
        "confidence": 82,
    },
    {
        "id": "C8",
        "name": "Increasing Leverage",
        "text": "Debt-to-equity ratio has increased over recent years.",
        "confidence": 82,
    },
    {
        "id": "C9",
        "name": "Weak EPS Trend",
        "text": "Declining earnings per share reflects deteriorating profitability.",
        "confidence": 85,
    },
    {
        "id": "C10",
        "name": "Low ROCE",
        "text": "Low return on capital employed suggests poor capital efficiency.",
        "confidence": 90,
    },
    {
        "id": "C11",
        "name": "High Leverage",
        "text": "High debt relative to operating earnings limits financial flexibility.",
        "confidence": 88,
    },
    {
        "id": "C12",
        "name": "Weak Revenue CAGR",
        "text": "Low revenue growth suggests limited long-term business momentum.",
        "confidence": 82,
    },
    {
        "id": "C13",
        "name": "Low Dividend Payout",
        "text": "Dividend payout remains relatively low, limiting cash returns to shareholders.",
        "confidence": 70,
    },
    {
        "id": "C14",
        "name": "Low Asset Turnover",
        "text": "Asset turnover remains below 1, indicating comparatively lower asset utilization.",
        "confidence": 68,
    },
    {
        "id": "C15",
        "name": "Low Book Value",
        "text": "Book value per share is relatively low compared with peers.",
        "confidence": 65,
    }
]