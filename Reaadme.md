# 🛒 Retail Intelligence Platform

> An end-to-end data analytics project built using Snowflake, SQL, VS Code, Python, Streamlit, and Medallion Architecture.

---

## 📌 Project Overview

The **Retail Intelligence Platform** is a mini end-to-end data engineering and analytics project designed to demonstrate how a large-scale retail dataset can be transformed into business-ready insights and exposed through an interactive application.

The project uses a large retail dataset available through Snowflake's sample data environment.

Instead of processing the entire dataset, the project intentionally extracts and processes only a relevant subset of the available data.

The selected data is then processed through a simplified **Medallion Architecture**:

```text
Snowflake Sample Dataset
          │
          ▼
     Data Selection
          │
          ▼
      🥉 BRONZE
    Raw Selected Data
          │
          ▼
       🥈 SILVER
 Cleaned & Standardized Data
          │
          ▼
        🥇 GOLD
 Business-Ready Data
          │
          ▼
      Python / SQL
          │
          ▼
      Streamlit App
          │
          ▼
     Business Users
