# Nifty 100 Financial Intelligence Platform

> An end-to-end financial analytics platform for analyzing, comparing, screening, and reporting on companies in the Nifty 100 index.

The **Nifty 100 Financial Intelligence Platform** is a Python-based financial analytics system that combines **data engineering, financial analysis, valuation analytics, stock screening, peer benchmarking, sector analysis, capital allocation analysis, automated reporting, REST APIs, and interactive visualization** into a single platform.

The system processes structured financial data for **92 Nifty 100 companies**, covering **30+ financial KPIs across 11 sectors**, and makes the resulting insights accessible through an interactive **Streamlit dashboard** and a **FastAPI REST API**.

---

## Project Objectives

The project was developed to transform raw financial data into a structured analytical system capable of answering questions such as:

- How financially healthy is a company?
- How does a company compare with its peers?
- Is a company's valuation relatively attractive within its sector?
- Which companies satisfy specific financial screening criteria?
- How have revenue, profitability, cash flow, and other financial metrics changed over time?
- How do financial characteristics differ across sectors?
- How efficiently is a company allocating capital?
- How can financial insights be generated consistently from structured data?

The goal was not simply to build a visualization dashboard, but to develop a complete workflow from **data preparation → storage → analytics → APIs → visualization → reporting**.

---

## Key Features

### Financial Analytics

- Multi-year financial statement analysis
- Revenue and profitability trends
- Financial ratio calculations
- CAGR calculations
- Historical KPI analysis
- Company-level financial profiling

### Valuation Analytics

- Price-to-Earnings (P/E)
- Price-to-Book (P/B)
- EV/EBITDA
- Free Cash Flow Yield
- Sector-level valuation comparison
- Automated valuation classification and flagging

### Stock Screener

A configurable screening engine supporting **18 financial screening criteria**, allowing companies to be filtered using metrics such as:

- P/E
- ROE
- Debt/Equity
- Market Capitalization
- Profitability metrics
- Growth metrics
- Valuation metrics
- Cash-flow related measures

Screening criteria can be configured and combined to create customized investment research queries.

### Peer Comparison

- Company-to-company benchmarking
- Sector peer identification
- Comparative financial metrics
- Peer averages
- Interactive radar-chart visualization

### Sector Analysis

- Sector-level aggregation
- Cross-sector financial comparisons
- Valuation comparisons
- Sector distributions
- Identification of sector leaders and relative differences

### Capital Allocation Analysis

Analysis of how companies deploy and generate capital through:

- Capital expenditure (CapEx)
- Free Cash Flow
- Dividend distributions
- Share buybacks
- Historical capital allocation trends

### Automated Reporting

The platform includes automated financial reporting utilities for generating structured company-level financial summaries and **financial tear sheets** from processed data.

### REST API

A FastAPI backend exposes financial data and analytical functionality through REST endpoints, with automatically generated Swagger documentation.

### Structured Data Layer

Financial data is transformed from raw source files into cleaned datasets and stored in a structured **SQLite database**, providing a consistent data layer for analytics, APIs, and dashboards.

### Testing & Data Quality

The project includes automated testing using **Pytest** covering analytical functions, API functionality, and data-quality checks.

---

# System Architecture

```text
                         ┌──────────────────────┐
                         │    Raw Financial     │
                         │        Data          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      ETL Pipeline    │
                         │                      │
                         │ Extract              │
                         │ Transform / Clean    │
                         │ Validate             │
                         │ Load                 │
                         └──────────┬───────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │      Processed Datasets      │
                    │          + SQLite             │
                    └──────────────┬───────────────┘
                                   │
                  ┌────────────────┼────────────────┐
                  │                │                │
                  ▼                ▼                ▼
          ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
          │   Analytics  │ │   Screener   │ │  Reporting   │
          │              │ │              │ │              │
          │ Ratios       │ │ 18 Filters  │ │ Tear Sheets  │
          │ CAGR         │ │ Custom Rules │ │ Summaries    │
          │ Valuation    │ │              │ │              │
          │ Clustering   │ │              │ │              │
          └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
                 │                │                │
                 └────────────────┼────────────────┘
                                  │
                   ┌──────────────┴──────────────┐
                   │                             │
                   ▼                             ▼
          ┌─────────────────┐          ┌─────────────────┐
          │ Streamlit       │          │ FastAPI         │
          │ Dashboard       │          │ REST API        │
          └─────────────────┘          └─────────────────┘
```

---

# Data Pipeline

The platform follows a structured financial data pipeline:

### 1. Extraction

Raw financial information is sourced from structured financial datasets, primarily maintained in spreadsheet/file formats.

### 2. Transformation

The ETL layer performs tasks such as:

- Data cleaning
- Standardization
- Type conversion
- Missing-value handling
- Financial metric preparation
- Company-level data organization

### 3. Validation

Data-quality checks are applied before analytical processing to identify inconsistencies and invalid records.

### 4. Storage

Cleaned financial information is stored in:

- Processed CSV datasets
- SQLite database tables

The database schema is documented through the project's SQL schema and data dictionary.

### 5. Analytics

The processed data feeds the project's:

- Financial ratio calculations
- CAGR calculations
- Valuation analytics
- Peer analysis
- Sector analysis
- Capital allocation analysis
- Screening engine
- Reporting utilities

### 6. Presentation

The analytical layer is exposed through both:

- Streamlit dashboard
- FastAPI REST API

---

# Dashboard

The Streamlit application contains **8 interactive modules**.

### 01 — Home Dashboard

Provides an executive-level overview of the platform and market data with navigation to the analytical modules.

### 02 — Company Profile

Provides a detailed financial profile for an individual company, including financial KPIs, company information, and related market references.

### 03 — Stock Screener

Allows users to apply configurable financial criteria to identify companies matching selected thresholds.

### 04 — Peer Comparison

Compares companies against relevant peers using financial metrics and interactive radar-chart visualizations.

### 05 — Financial Trends

Provides multi-year analysis of:

- Revenue
- Growth
- Profitability
- Financial ratios
- Other historical KPIs

### 06 — Sector Analysis

Analyzes financial characteristics across the **11 sectors** represented in the project's dataset.

### 07 — Capital Allocation

Examines:

- CapEx
- Free Cash Flow
- Dividends
- Buybacks
- Capital deployment trends

### 08 — Reports & Outputs

Provides access to analytical summaries, downloadable data, and generated reporting outputs.

---

# FastAPI REST API

The platform includes a REST API built with **FastAPI**.

| Router | Endpoint | Purpose |
|---|---|---|
| Health | `GET /api/v1/health` | Check API and database status |
| Companies | `GET /api/v1/companies` | Retrieve Nifty 100 company information |
| Company Detail | `GET /api/v1/companies/{id}` | Retrieve detailed company information |
| Screener | `POST /api/v1/screener/run` | Execute screening criteria |
| Valuation | `GET /api/v1/valuation` | Retrieve valuation metrics and classifications |
| Peers | `GET /api/v1/peers/{symbol}` | Retrieve peer comparison data |
| Market Cap | `GET /api/v1/market-cap` | Retrieve market-cap rankings/breakdowns |
| Sectors | `GET /api/v1/sectors` | Retrieve sector-level financial aggregates |

When the API server is running, interactive Swagger documentation is available at:

```text
http://localhost:8000/docs
```

## Application URLs & Access Links

| Service | Access URL | Description |
| :--- | :--- | :--- |
| **Streamlit Interactive Dashboard** | [http://localhost:8501](http://localhost:8501) | Primary 8-Page Web Interface |
| **FastAPI REST API Server** | [http://localhost:8000](http://localhost:8000) | High-Performance REST API Backend |
| **Interactive API Documentation (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger UI for API Endpoint Testing |
| **Alternative API Docs (ReDoc)** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | ReDoc API Technical Specification |

*Note: If deployed on cloud platforms like Streamlit Community Cloud or Render/AWS, replace `http://localhost:8501` with your deployed live URL (e.g. `https://your-app-name.streamlit.app`).*

---

# Analytics Layer

The core analytics layer is organized into dedicated modules.

### Financial Ratios

Calculates and prepares financial ratios used throughout the platform.

### Valuation

Provides valuation metrics and relative valuation classification.

### CAGR

Calculates compound annual growth rates for applicable multi-year financial metrics.

### Clustering

Provides analytical grouping functionality using Scikit-Learn-based clustering techniques.

### Screener

Implements configurable multi-metric financial screening logic.

### Reporting

Transforms analytical results into structured financial summaries and reporting outputs.

---

# Database

The project uses **SQLite** as its structured financial data backend.

```text
data/
└── database/
    ├── nifty100.db
    └── schema.sql
```

The database acts as the central structured data layer used by the analytical and API components.

A separate data dictionary is maintained under the documentation directory to describe the project's financial fields and schema.

---

# Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python 3.10+ |
| Data Processing | Pandas, NumPy |
| Financial Analytics | Pandas, NumPy, Scikit-Learn |
| Dashboard | Streamlit |
| Visualization | Plotly |
| REST API | FastAPI |
| API Server | Uvicorn |
| Data Validation / Models | Pydantic |
| Database | SQLite |
| Spreadsheet Processing | OpenPyXL |
| Configuration | PyYAML |
| Testing | Pytest, Pytest-HTML |
| Code Quality | Ruff |
| Version Control | Git, GitHub |

---

# Project Structure

```text
nifty100-financial-intelligence-platform/
│
├── config/
│   └── screener_config.yaml
│
├── data/
│   ├── database/
│   │   ├── nifty100.db
│   │   └── schema.sql
│   │
│   ├── raw/
│   │   └── raw financial datasets
│   │
│   └── processed/
│       └── cleaned financial datasets
│
├── docs/
│   ├── screenshots/
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── Postman_collection.json
│
├── notebooks/
│   └── exploratory analysis & research
│
├── output/
│   └── generated exports & summaries
│
├── reports/
│   └── generated reports
│
├── src/
│   ├── analytics/
│   │   ├── ratios.py
│   │   ├── valuation.py
│   │   ├── cagr.py
│   │   └── clustering.py
│   │
│   ├── api/
│   │   ├── main.py
│   │   └── routers/
│   │
│   ├── dashboard/
│   │   ├── app.py
│   │   └── pages/
│   │
│   ├── etl/
│   │
│   ├── reporting/
│   │
│   ├── screener/
│   │
│   └── utils/
│
├── tests/
│   ├── api/
│   └── test_*.py
│
├── requirements.txt
├── pytest.ini
└── README.md
```

---

# Installation & Setup

## Prerequisites

- Python **3.10+**
- Git
- pip

## 1. Clone the Repository

```bash
git clone https://github.com/hardikj1508/nifty100-financial-intelligence-platform.git

cd nifty100-financial-intelligence-platform
```

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv n100env

n100env\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv n100env

source n100env/bin/activate
```

## 3. Install Dependencies

Install the project's defined dependencies:

```bash
pip install -r requirements.txt
```

---

# Running the Platform

## Streamlit Dashboard

From the project root:

```bash
streamlit run src/dashboard/app.py
```

The dashboard will be available at:

```text
http://localhost:8501
```

---

## FastAPI Backend

Start the API server with:

```bash
uvicorn src.api.main:app --reload --port 8000
```

API:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

---

# Testing

Run the complete test suite:

```bash
pytest
```

Generate an HTML test report:

```bash
pytest --html=reports/test_report.html
```

The test suite covers analytical functionality, API components, and data-quality checks.

---

# Dashboard Screenshots

The repository contains screenshots of the completed dashboard under:

```text
docs/screenshots/
```

Available modules include:

| Module | Screenshot |
|---|---|
| Home Dashboard | `docs/screenshots/01_home.png` |
| Company Profile | `docs/screenshots/02_profile.png` |
| Stock Screener | `docs/screenshots/03_screener.png` |
| Peer Comparison | `docs/screenshots/04_peer_comparison.png` |
| Financial Trends | `docs/screenshots/05_financial_trends.png` |
| Sector Analysis | `docs/screenshots/06_sector_analysis.png` |
| Capital Allocation | `docs/screenshots/07_capital_allocation.png` |
| Reports | `docs/screenshots/08_reports.png` |

---

# Project Scope

The completed platform covers:

| Area | Scope |
|---|---:|
| Companies analyzed | 92 |
| Financial KPIs | 30+ |
| Sectors | 11 |
| Screener criteria | 18 |
| Dashboard modules | 8 |
| Data storage | SQLite + processed datasets |
| Interfaces | Streamlit + FastAPI |
| Testing | Pytest-based automated test suite |

---

# Skills Demonstrated

This project brings together several areas of practical data and software engineering:

### Data Analytics

- Exploratory data analysis
- Financial KPI analysis
- Trend analysis
- Comparative analysis
- Ratio analysis

### Financial Analytics

- Valuation metrics
- Profitability analysis
- Growth analysis
- Capital allocation
- Peer benchmarking
- Sector analysis

### Data Engineering

- ETL pipeline development
- Data cleaning
- Data validation
- Structured data storage
- SQLite database design

### Python Development

- Modular project architecture
- Reusable analytical functions
- Configuration-driven logic
- API development
- Automated testing

### Visualization

- Interactive Plotly visualizations
- Streamlit dashboards
- Radar charts
- Financial trend visualizations
- Sector comparisons

### Software Engineering

- REST API design
- Unit and integration testing
- Code organization
- Git/GitHub workflow
- Documentation

---

# Limitations

The current platform is primarily an **analytical and research system**, rather than a live trading platform.

Current limitations include:

- Financial data is dependent on the available underlying datasets.
- The platform does not currently provide a live real-time market-data feed.
- Valuation analysis is based on the implemented financial metrics and relative comparisons rather than a complete investment valuation framework.
- Screening results should be interpreted as analytical outputs rather than investment recommendations.

---

# Future Enhancements

Potential extensions include:

- Live market-data integration
- Dynamic DCF valuation
- More comprehensive relative valuation models
- Portfolio creation and watchlist functionality
- Automated AI-assisted financial summaries
- Additional predictive analytics
- PDF report generation
- Expanded historical data coverage
- Deployment as a cloud-hosted financial analytics service

---

# Disclaimer

This project is intended for **educational, analytical, and research purposes**.

The financial metrics, screening outputs, valuation classifications, and other analytical results generated by the platform should **not be treated as financial advice or a recommendation to buy or sell securities**.

---

# Author

**Hardik Jain**

*B.Sc. Statistics (Hons.) — St. Xavier's College, Ranchi University*

**Areas of Interest**

- Data Analytics
- Data Engineering
- Financial Analytics
- Python Development
- Interactive Data Visualization

---

## Project Highlights

The Nifty 100 Financial Intelligence Platform demonstrates an end-to-end approach to building a financial analytics product:

```text
Raw Data
   ↓
ETL & Data Quality
   ↓
Processed Financial Data
   ↓
SQLite Database
   ↓
Financial Analytics
   ↓
Screening / Valuation / Peer / Sector Analysis
   ↓
Reporting
   ↓
FastAPI + Streamlit
   ↓
Interactive Financial Intelligence Platform
```

**Built as a practical portfolio project combining financial analysis, data engineering, Python development, visualization, API development, and software testing.**