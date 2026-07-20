# 📊 Nifty 100 Financial Intelligence Platform

A comprehensive financial analytics dashboard built using **Python**, **Streamlit**, **SQLite**, and **Pandas** for analyzing companies listed in the Nifty 100 index.

The platform provides investors and analysts with interactive dashboards to explore company financials, compare peers, evaluate sector performance, analyze capital allocation, monitor valuation metrics, and generate business insights through an intuitive web interface.

This project was developed as part of an internship to demonstrate skills in data engineering, financial analytics, data visualization, and dashboard development.

## 🚀 Features

- Interactive Streamlit dashboard for Nifty 100 company analysis
- Company Profile with key financial metrics and business information
- Advanced Stock Screener using customizable financial filters
- Peer Comparison with radar charts and benchmark analysis
- Multi-year Financial Trends visualization
- Sector-wise analysis and performance comparison
- Capital Allocation analysis (CapEx, Free Cash Flow, Dividends, Buybacks)
- Valuation Analytics
  - P/E Ratio
  - P/B Ratio
  - EV/EBITDA
  - Free Cash Flow Yield
  - Sector Median P/E Comparison
  - Valuation Flagging (Fair, Discount, Caution)
- Downloadable reports and summary outputs
- SQLite-powered backend for efficient data retrieval
- Interactive visualizations using Plotly
- Robust handling of missing and partial financial data

## 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| Programming Language | Python 3 |
| Dashboard | Streamlit |
| Database | SQLite |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| File Handling | OpenPyXL |
| Version Control | Git, GitHub |
| Development Environment | Visual Studio Code |

## 📂 Project Structure

```text
Nifty100-Financial-Intelligence-Platform/
│
├── config/                 # Configuration files
├── data/
│   ├── database/           # SQLite database
│   ├── raw/                # Raw financial datasets
│   └── processed/          # Cleaned datasets
│
├── docs/                   # Documentation and screenshots
├── notebooks/              # Development notebooks
├── output/                 # Generated reports and outputs
├── reports/                # Project reports
│
├── src/
│   ├── analytics/          # Financial analytics modules
│   ├── dashboard/
│   │   ├── pages/          # Streamlit pages
│   │   ├── utils/          # Dashboard utilities
│   │   └── app.py          # Dashboard entry point
│   ├── etl/                # Data extraction and transformation
│   ├── reporting/          # Report generation
│   ├── screener/           # Stock screener logic
│   └── utils/              # Shared utility functions
│
├── tests/                  # Unit tests
├── requirements.txt
├── README.md
└── .gitignore
```

## 📊 Dashboard Modules

The application consists of the following interactive modules:

### 🏠 Home
- Dashboard overview with key financial insights and navigation.

### 🏢 Company Profile
- Company information
- Key financial KPIs
- Business description
- Official website and exchange links

### 🔍 Stock Screener
- Filter companies using multiple financial metrics.
- Dynamic search and comparison capabilities.

### 🤝 Peer Comparison
- Compare companies within the same sector.
- Interactive radar chart for financial metrics.
- Peer average benchmarking.

### 📈 Financial Trends
- Multi-year trend analysis.
- Interactive charts for financial performance.

### 🏭 Sector Analysis
- Compare companies across different sectors.
- Sector-level financial insights.

### 💰 Capital Allocation
- Analyze:
  - Capital Expenditure (CapEx)
  - Free Cash Flow
  - Dividends
  - Share Buybacks

### 📑 Reports
- Download processed reports.
- Access project documentation and summary outputs.

### 💹 Valuation Analytics
- Price-to-Earnings (P/E)
- Price-to-Book (P/B)
- EV/EBITDA
- Free Cash Flow Yield
- Sector Median P/E Comparison
- Valuation Classification (Fair, Discount, Caution)

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/hardikj1508/nifty100-financial-intelligence-platform.git
cd nifty100-financial-intelligence-platform
```

### 2. Create a Virtual Environment (Optional)

If you don't already have a virtual environment:

```bash
python -m venv n100env
```

### 3. Activate the Virtual Environment

**Windows**

```bash
n100env\Scripts\activate
```

**Linux / macOS**

```bash
source n100env/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
streamlit run app.py
```

## ✅ Section 7 — Project Outputs

Now let's show what the project generates.

```markdown
## 📁 Project Outputs

The project generates various analytical outputs, including:

- Valuation Summary Report
- Valuation Flags
- Financial Trend Analysis
- Capital Allocation Insights
- Interactive Dashboard Visualizations
- Downloadable Reports

## 📸 Dashboard Preview

### 🏠 Home Dashboard

Interactive overview of the Nifty 100 Financial Intelligence Platform.

![Home Dashboard](docs/screenshots/01_home.png)

---

### 🏢 Company Profile

View company information, KPIs, business details, and market links.

![Company Profile](docs/screenshots/02_profile.png)

---

### 🔍 Stock Screener

Filter companies using multiple financial metrics.

![Stock Screener](docs/screenshots/03_screener.png)

---

### 🤝 Peer Comparison

Compare companies with sector peers using interactive radar charts.

![Peer Comparison](docs/screenshots/04_peer_comparison.png)

---

### 📈 Financial Trends

Analyze multi-year financial performance.

![Financial Trends](docs/screenshots/05_financial_trends.png)

---

### 🏭 Sector Analysis

Compare financial performance across sectors.

![Sector Analysis](docs/screenshots/06_sector_analysis.png)

---

### 💰 Capital Allocation

Review CapEx, Free Cash Flow, Dividends, and Buybacks.

![Capital Allocation](docs/screenshots/07_capital_allocation.png)

---

### 📑 Reports

Access downloadable reports and generated analytics.

![Reports](docs/screenshots/08_reports.png)

## 🚀 Future Enhancements

- Live stock market data integration
- Portfolio tracking dashboard
- Watchlist functionality
- Advanced valuation models (DCF, Relative Valuation)
- AI-powered financial insights
- Export reports to PDF
- User authentication and personalized dashboards

## 👨‍💻 Author

**Hardik Jain**

B.Sc. Statistics (Hons.)  
St. Xavier's College, Ranchi University

**Skills:** Python, SQL, SQLite, Pandas, NumPy, Streamlit, Plotly, Data Analysis, Financial Analytics
