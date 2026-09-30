# AdventureWorks DW Medallion Lakehouse Architecture

## Executive Summary
This project implements a scalable **Medallion Lakehouse Architecture** on Google Cloud Platform (GCP) for the standard **AdventureWorksDW** sample data warehouse.

- **Cloud Provider**: Google Cloud Platform (GCP)
- **Region**: London (`europe-west2`)
- **Engine**: Google BigQuery
- **Ingestion**: Google Cloud Dataflow (Apache Beam, Python 3.12)
- **Transformation**: `dbt` (`dbt-bigquery`)
- **Source**: Microsoft AdventureWorksDW (Pipe-delimited CSVs)

---

## Architecture Flow

```mermaid
flowchart TD
    subgraph Storage["Google Cloud Storage (europe-west2)"]
        GCS["gs://{project}-adventureworks-raw-london/raw/adventureworks/*.csv"]
    end

    subgraph Dataflow["Cloud Dataflow Ingestion Engine (Python 3.12)"]
        Parser["Apache Beam Pipeline\n• Pipe-delimited parsing\n• Null standardisation\n• Audit metadata tagging\n• Dead-Letter Queue (DLQ)"]
    end

    subgraph Medallion["Google BigQuery (europe-west2)"]
        subgraph Bronze["🥉 Bronze Layer (adventureworks_bronze)"]
            B1["Raw Source-Fidelity Tables (28 tables)\n• DimAccount, DimCustomer, DimProduct...\n• FactInternetSales, FactResellerSales..."]
        end

        subgraph Silver["🥈 Silver Layer (adventureworks_silver)"]
            S1["Conformed Dims & Cleaned Facts\n• dim_customers, dim_products, dim_dates...\n• fact_internet_sales, fact_reseller_sales...\n• Partitioned on Dates & Clustered on Keys"]
        end

        subgraph Gold["🥇 Gold Layer (adventureworks_gold)"]
            G1["📊 mart_sales_executive_overview\n(Omni-channel sales, profit margins, growth)"]
            G2["👥 mart_customer_360_rfm\n(Customer RFM segmentation, LTV, repeat rates)"]
            G3["📦 mart_inventory_supply_chain\n(Stockout risk, reorder alerts, inventory valuation)"]
            G4["💼 mart_sales_rep_quota_performance\n(Quota attainment %, rep rankings)"]
            G5["💰 mart_finance_pnl_summary\n(Actual vs Budget variance, OPEX rollups)"]
        end
    end

    GCS --> Parser
    Parser --> Bronze
    Bronze -->|dbt run (Silver Models)| Silver
    Silver -->|dbt run (Gold Marts)| Gold
```

---

## Medallion Layers

### 1. 🥉 Bronze (`adventureworks_bronze`)
- **Role**: Raw data ingestion.
- **Design**: Exact high-fidelity replica of the 28 source tables.
- **Audit Columns**:
  - `_ingested_at`: UTC timestamp of the ingestion run.
  - `_source_file`: GCS file URI of origin.
  - `_raw_row_id`: Unique row UUID generated during ingestion.

### 2. 🥈 Silver (`adventureworks_silver`)
- **Role**: Cleaned, conformed, and typed dimensional model.
- **Transformations**:
  - Strongly typed data formats (`DATE`, `NUMERIC`, `INT64`, `BOOLEAN`).
  - Standardized surrogate keys and null strings.
  - Performance optimization via **Date Partitioning** and **High-Cardinality Key Clustering**.

### 3. 🥇 Gold (`adventureworks_gold`)
- **Role**: Curated analytical business marts designed for BI reporting (Looker/PowerBI) and ML modeling.
- **Core Marts**:
  - `mart_sales_executive_overview`: Omni-channel sales combining Internet and Reseller channels with margin KPIs.
  - `mart_customer_360_rfm`: RFM segmentation into *Champions, Loyal, At Risk, Lost*, customer LTV, and demographics.
  - `mart_inventory_supply_chain`: Inventory valuation, stockout warnings, and reorder point alerts.
  - `mart_sales_rep_quota_performance`: Sales rep performance vs quarterly quotas and attainment %.
  - `mart_finance_pnl_summary`: General ledger actual vs. budget financial variances.
