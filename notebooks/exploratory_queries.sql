-- Query 1
SELECT COUNT(*) AS total_companies
FROM companies;

-- Query 2
SELECT
    company_id,
    market_cap_crore
FROM market_cap
ORDER BY market_cap_crore DESC
LIMIT 10;

-- Query 3
SELECT
    company_id,
    year,
    net_profit
FROM profitandloss
ORDER BY net_profit DESC
LIMIT 10;

-- Query 4
SELECT
    company_id,
    year,
    sales
FROM profitandloss
ORDER BY sales DESC
LIMIT 10;

-- Query 5
SELECT
    company_id,
    year,
    net_cash_flow
FROM cashflow
WHERE net_cash_flow < 0;

-- Query 6
SELECT
    broad_sector,
    COUNT(*) AS companies
FROM sectors
GROUP BY broad_sector
ORDER BY companies DESC;

-- Query 7
SELECT
    company_id,
    return_on_equity_pct
FROM financial_ratios
ORDER BY return_on_equity_pct DESC
LIMIT 10;

-- Query 8
SELECT
    company_id,
    COUNT(DISTINCT year) AS years_available
FROM profitandloss
GROUP BY company_id
HAVING COUNT(DISTINCT year) < 5;

-- Query 9
SELECT 'companies', COUNT(*) FROM companies
UNION ALL
SELECT 'profitandloss', COUNT(*) FROM profitandloss
UNION ALL
SELECT 'balancesheet', COUNT(*) FROM balancesheet
UNION ALL
SELECT 'cashflow', COUNT(*) FROM cashflow;

-- Query 10
PRAGMA foreign_key_check;

