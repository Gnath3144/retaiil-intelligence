-- ==============================================================================
-- SILVER LAYER: Cleaned, Typed, Deduplicated Conformed Data
-- Database: MEDICAPS_RETAIL
-- Schema: SILVER
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS MEDICAPS_RETAIL.SILVER;

-- 1. Create Cleaned Silver Sales Fact Table
CREATE OR REPLACE TABLE MEDICAPS_RETAIL.SILVER.SALES AS
SELECT
    SS_SOLD_DATE_SK       AS DATE_KEY,
    SS_ITEM_SK            AS ITEM_KEY,
    SS_STORE_SK           AS STORE_KEY,
    SS_CUSTOMER_SK        AS CUSTOMER_KEY,
    SS_QUANTITY           AS QUANTITY,
    SS_SALES_PRICE        AS SALES_PRICE,
    COALESCE(SS_EXT_SALES_PRICE, (SS_QUANTITY * SS_SALES_PRICE)) AS TOTAL_SALES
FROM MEDICAPS_RETAIL.BRONZE.STORE_SALES
WHERE SS_SOLD_DATE_SK IS NOT NULL
  AND SS_ITEM_SK IS NOT NULL
  AND SS_QUANTITY > 0
  AND SS_SALES_PRICE > 0;
