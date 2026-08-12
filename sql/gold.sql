-- ==============================================================================
-- GOLD LAYER: Aggregated Business Marts & Analytics Tables
-- Database: MEDICAPS_RETAIL
-- Schema: GOLD
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS MEDICAPS_RETAIL.GOLD;

-- 1. Create Sales by Category / Item Mart
CREATE OR REPLACE TABLE MEDICAPS_RETAIL.GOLD.SALES_BY_CATEGORY AS
SELECT
    ITEM_KEY,
    SUM(TOTAL_SALES)                 AS TOTAL_REVENUE,
    SUM(QUANTITY)                    AS TOTAL_UNITS,
    COUNT(*)                         AS TOTAL_TRANSACTIONS,
    AVG(TOTAL_SALES)                 AS AVERAGE_TRANSACTION_VALUE
FROM MEDICAPS_RETAIL.SILVER.SALES
GROUP BY ITEM_KEY
ORDER BY TOTAL_REVENUE DESC;

-- 2. Create Top Products Leaderboard Mart
CREATE OR REPLACE TABLE MEDICAPS_RETAIL.GOLD.TOP_PRODUCTS AS
WITH ProductTotals AS (
    SELECT
        ITEM_KEY,
        SUM(TOTAL_SALES) AS TOTAL_REVENUE
    FROM MEDICAPS_RETAIL.SILVER.SALES
    GROUP BY ITEM_KEY
)
SELECT
    ITEM_KEY,
    TOTAL_REVENUE,
    DENSE_RANK() OVER (ORDER BY TOTAL_REVENUE DESC) AS PRODUCT_RANK
FROM ProductTotals
ORDER BY PRODUCT_RANK ASC;
