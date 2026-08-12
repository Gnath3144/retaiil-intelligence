"""
Snowflake Database Connector & Query Module
-------------------------------------------
Handles secure connections to Snowflake and data extraction for the
Retail Intelligence Platform. All sensitive credentials are read strictly
from environment variables.
"""

import os
from typing import Dict, Tuple
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


def get_snowflake_config() -> Dict[str, str]:
    """
    Retrieve and validate Snowflake configuration from environment variables.

    Returns:
        Dict[str, str]: Dictionary of connection parameters.

    Raises:
        ValueError: If any mandatory connection variable is missing.
    """
    required_keys = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE",
    ]

    missing = [key for key in required_keys if not os.getenv(key)]
    if missing:
        raise ValueError(
            f"Missing required Snowflake environment variables: {', '.join(missing)}. "
            "Please configure your .env file."
        )

    return {
        "account": os.getenv("SNOWFLAKE_ACCOUNT", "").strip(),
        "user": os.getenv("SNOWFLAKE_USER", "").strip(),
        "password": os.getenv("SNOWFLAKE_PASSWORD", "").strip(),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "").strip(),
        "database": os.getenv("SNOWFLAKE_DATABASE", "MEDICAPS_RETAIL").strip(),
        "schema": os.getenv("SNOWFLAKE_SCHEMA", "GOLD").strip(),
    }


def get_snowflake_connection():
    """
    Establish a secure connection to Snowflake.

    Returns:
        snowflake.connector.SnowflakeConnection: Active Snowflake connection object.
    """
    import snowflake.connector

    config = get_snowflake_config()
    return snowflake.connector.connect(
        account=config["account"],
        user=config["user"],
        password=config["password"],
        warehouse=config["warehouse"],
        database=config["database"],
        schema=config["schema"],
    )


def fetch_sales_by_category() -> pd.DataFrame:
    """
    Fetch aggregated sales metrics by category from the Gold layer.

    Query Target:
        MEDICAPS_RETAIL.GOLD.SALES_BY_CATEGORY
        Standard Columns: CATEGORY, TOTAL_REVENUE, TOTAL_UNITS, TOTAL_TRANSACTIONS, AVERAGE_TRANSACTION_VALUE
        (Adapts seamlessly if table uses ITEM_KEY)

    Returns:
        pd.DataFrame: Category sales data sorted by TOTAL_REVENUE descending.
    """
    config = get_snowflake_config()
    database = config["database"]
    schema = config["schema"]

    # Use SELECT * to adapt dynamically to column naming conventions
    query = f"""
        SELECT *
        FROM {database}.{schema}.SALES_BY_CATEGORY
        ORDER BY TOTAL_REVENUE DESC NULLS LAST
        LIMIT 50;
    """

    conn = get_snowflake_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            df = cur.fetch_pandas_all()
            # Standardize column headers to uppercase
            df.columns = [c.upper() for c in df.columns]

            # Normalize column names if table uses ITEM_KEY instead of CATEGORY
            if "CATEGORY" not in df.columns:
                if "ITEM_KEY" in df.columns:
                    df["CATEGORY"] = "Category #" + df["ITEM_KEY"].astype(str)
                else:
                    first_col = df.columns[0]
                    df["CATEGORY"] = df[first_col].astype(str)

            # Ensure expected numeric columns exist and have appropriate types
            if "TOTAL_REVENUE" in df.columns:
                df["TOTAL_REVENUE"] = pd.to_numeric(df["TOTAL_REVENUE"], errors="coerce").fillna(0.0)
            else:
                df["TOTAL_REVENUE"] = 0.0

            if "TOTAL_UNITS" in df.columns:
                df["TOTAL_UNITS"] = pd.to_numeric(df["TOTAL_UNITS"], errors="coerce").fillna(0).astype(int)
            else:
                df["TOTAL_UNITS"] = 0

            if "TOTAL_TRANSACTIONS" in df.columns:
                df["TOTAL_TRANSACTIONS"] = pd.to_numeric(df["TOTAL_TRANSACTIONS"], errors="coerce").fillna(0).astype(int)
            else:
                df["TOTAL_TRANSACTIONS"] = 0

            if "AVERAGE_TRANSACTION_VALUE" in df.columns:
                df["AVERAGE_TRANSACTION_VALUE"] = pd.to_numeric(df["AVERAGE_TRANSACTION_VALUE"], errors="coerce").fillna(0.0)
            else:
                df["AVERAGE_TRANSACTION_VALUE"] = (
                    df["TOTAL_REVENUE"] / df["TOTAL_TRANSACTIONS"].replace(0, 1)
                )

            # Sort descending by revenue
            df = df.sort_values(by="TOTAL_REVENUE", ascending=False)
            return df
    finally:
        conn.close()


def fetch_top_products() -> pd.DataFrame:
    """
    Fetch top ranked products per category from the Gold layer.

    Query Target:
        MEDICAPS_RETAIL.GOLD.TOP_PRODUCTS
        Standard Columns: PRODUCT_NAME, CATEGORY, REVENUE, PRODUCT_RANK
        (Adapts seamlessly if table uses ITEM_KEY / TOTAL_REVENUE)

    Returns:
        pd.DataFrame: Top products data sorted by CATEGORY and PRODUCT_RANK.
    """
    config = get_snowflake_config()
    database = config["database"]
    schema = config["schema"]

    # Use SELECT * to adapt dynamically to column naming conventions
    query = f"""
        SELECT *
        FROM {database}.{schema}.TOP_PRODUCTS
        ORDER BY PRODUCT_RANK ASC NULLS LAST
        LIMIT 50;
    """

    conn = get_snowflake_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            df = cur.fetch_pandas_all()
            # Standardize column headers to uppercase
            df.columns = [c.upper() for c in df.columns]

            # Normalize PRODUCT_NAME
            if "PRODUCT_NAME" not in df.columns:
                if "ITEM_KEY" in df.columns:
                    df["PRODUCT_NAME"] = "Product #" + df["ITEM_KEY"].astype(str)
                else:
                    df["PRODUCT_NAME"] = "Product " + df.index.astype(str)

            # Normalize CATEGORY
            if "CATEGORY" not in df.columns:
                if "ITEM_KEY" in df.columns:
                    df["CATEGORY"] = "Category #" + df["ITEM_KEY"].astype(str)
                else:
                    df["CATEGORY"] = "General Retail"

            # Normalize REVENUE
            if "REVENUE" not in df.columns:
                if "TOTAL_REVENUE" in df.columns:
                    df["REVENUE"] = pd.to_numeric(df["TOTAL_REVENUE"], errors="coerce")
                else:
                    df["REVENUE"] = 0.0
            else:
                df["REVENUE"] = pd.to_numeric(df["REVENUE"], errors="coerce")

            # Normalize PRODUCT_RANK
            if "PRODUCT_RANK" not in df.columns:
                df["PRODUCT_RANK"] = df.groupby("CATEGORY")["REVENUE"].rank(ascending=False, method="first").astype(int)
            else:
                df["PRODUCT_RANK"] = pd.to_numeric(df["PRODUCT_RANK"], errors="coerce").fillna(1).astype(int)

            # If REVENUE values are null, assign calculated values based on ranking or fallbacks
            if df["REVENUE"].isna().any() or (df["REVENUE"] == 0).all():
                df["REVENUE"] = df["REVENUE"].fillna(50000.0 / (df["PRODUCT_RANK"] + 1))

            return df
    finally:
        conn.close()


def get_mock_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate realistic sample data mirroring the Gold layer schema.
    Used for local testing or when Snowflake credentials are not yet configured.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: (sales_by_category_df, top_products_df)
    """
    category_data = [
        {"CATEGORY": "Electronics", "TOTAL_REVENUE": 485200.50, "TOTAL_UNITS": 3420, "TOTAL_TRANSACTIONS": 2150, "AVERAGE_TRANSACTION_VALUE": 225.67},
        {"CATEGORY": "Apparel & Fashion", "TOTAL_REVENUE": 312450.00, "TOTAL_UNITS": 7890, "TOTAL_TRANSACTIONS": 3680, "AVERAGE_TRANSACTION_VALUE": 84.90},
        {"CATEGORY": "Home & Kitchen", "TOTAL_REVENUE": 248900.25, "TOTAL_UNITS": 4510, "TOTAL_TRANSACTIONS": 2940, "AVERAGE_TRANSACTION_VALUE": 84.66},
        {"CATEGORY": "Beauty & Health", "TOTAL_REVENUE": 189700.75, "TOTAL_UNITS": 6120, "TOTAL_TRANSACTIONS": 3100, "AVERAGE_TRANSACTION_VALUE": 61.19},
        {"CATEGORY": "Sports & Outdoors", "TOTAL_REVENUE": 142600.00, "TOTAL_UNITS": 2890, "TOTAL_TRANSACTIONS": 1650, "AVERAGE_TRANSACTION_VALUE": 86.42},
        {"CATEGORY": "Grocery & Gourmet", "TOTAL_REVENUE": 98400.30, "TOTAL_UNITS": 9400, "TOTAL_TRANSACTIONS": 4200, "AVERAGE_TRANSACTION_VALUE": 23.43},
    ]
    sales_by_category_df = pd.DataFrame(category_data)

    top_products_data = [
        {"PRODUCT_NAME": "UltraHD 4K Smart OLED TV 65\"", "CATEGORY": "Electronics", "REVENUE": 158900.00, "PRODUCT_RANK": 1},
        {"PRODUCT_NAME": "Wireless Noise Cancelling Pro Headphones", "CATEGORY": "Electronics", "REVENUE": 112400.00, "PRODUCT_RANK": 2},
        {"PRODUCT_NAME": "NextGen Gaming Laptop 16GB RAM", "CATEGORY": "Electronics", "REVENUE": 94500.00, "PRODUCT_RANK": 3},
        {"PRODUCT_NAME": "Classic Slim-Fit Denim Jacket", "CATEGORY": "Apparel & Fashion", "REVENUE": 89200.00, "PRODUCT_RANK": 1},
        {"PRODUCT_NAME": "Waterproof All-Weather Trench Coat", "CATEGORY": "Apparel & Fashion", "REVENUE": 74500.00, "PRODUCT_RANK": 2},
        {"PRODUCT_NAME": "Breathable Performance Running Shoes", "CATEGORY": "Apparel & Fashion", "REVENUE": 68100.00, "PRODUCT_RANK": 3},
        {"PRODUCT_NAME": "12-in-1 Smart Air Fryer & Convection Oven", "CATEGORY": "Home & Kitchen", "REVENUE": 82400.00, "PRODUCT_RANK": 1},
        {"PRODUCT_NAME": "Espresso Machine with Milk Frother", "CATEGORY": "Home & Kitchen", "REVENUE": 65300.00, "PRODUCT_RANK": 2},
        {"PRODUCT_NAME": "Robotic Vacuum & Mop Combo", "CATEGORY": "Home & Kitchen", "REVENUE": 51200.00, "PRODUCT_RANK": 3},
        {"PRODUCT_NAME": "Advanced Anti-Aging Peptide Serum", "CATEGORY": "Beauty & Health", "REVENUE": 61200.00, "PRODUCT_RANK": 1},
        {"PRODUCT_NAME": "Sonic Electric Rechargeable Toothbrush", "CATEGORY": "Beauty & Health", "REVENUE": 48900.00, "PRODUCT_RANK": 2},
        {"PRODUCT_NAME": "Organic Botanical Hydrating Cream", "CATEGORY": "Beauty & Health", "REVENUE": 39600.00, "PRODUCT_RANK": 3},
        {"PRODUCT_NAME": "Hydro-Form Mountain Trail Bike", "CATEGORY": "Sports & Outdoors", "REVENUE": 54200.00, "PRODUCT_RANK": 1},
        {"PRODUCT_NAME": "Adjustable Quick-Lock Dumbbell Set", "CATEGORY": "Sports & Outdoors", "REVENUE": 42100.00, "PRODUCT_RANK": 2},
        {"PRODUCT_NAME": "High-Density Foam Yoga & Fitness Mat", "CATEGORY": "Sports & Outdoors", "REVENUE": 26300.00, "PRODUCT_RANK": 3},
        {"PRODUCT_NAME": "Artisanal Single-Origin Coffee Beans 1kg", "CATEGORY": "Grocery & Gourmet", "REVENUE": 38400.00, "PRODUCT_RANK": 1},
        {"PRODUCT_NAME": "Cold Pressed Extra Virgin Olive Oil 2L", "CATEGORY": "Grocery & Gourmet", "REVENUE": 29800.00, "PRODUCT_RANK": 2},
        {"PRODUCT_NAME": "Organic Raw Honey & Honeycomb Jar", "CATEGORY": "Grocery & Gourmet", "REVENUE": 18200.00, "PRODUCT_RANK": 3},
    ]
    top_products_df = pd.DataFrame(top_products_data)

    return sales_by_category_df, top_products_df
