# AdventureWorks DW Medallion Lakehouse on Google Cloud

[![CI Pipeline](https://github.com/SadeeqAkintola/adventure-works-medallion-project/actions/workflows/ci.yml/badge.svg)](https://github.com/SadeeqAkintola/adventure-works-medallion-project/actions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![BigQuery](https://img.shields.io/badge/Google_Cloud-BigQuery-4285F4?logo=google-cloud&logoColor=white)](https://cloud.google.com/bigquery)
[![Dataflow](https://img.shields.io/badge/Google_Cloud-Dataflow-FF6F00?logo=apache-beam&logoColor=white)](https://cloud.google.com/dataflow)
[![dbt](https://img.shields.io/badge/dbt-BigQuery-FF694B?logo=dbt&logoColor=white)](https://www.getdbt.com/)

A modern, enterprise-grade **Medallion Lakehouse (Bronze 🥉 $\rightarrow$ Silver 🥈 $\rightarrow$ Gold 🥇)** implementation on **Google BigQuery** in the **London region (`europe-west2`)**. 

It ingests the complete Microsoft **AdventureWorksDW** relational schema (28+ tables) using **Google Cloud Dataflow (Apache Beam)** and orchestrates conformed dimensional models and analytical business marts using **dbt-bigquery**.

---

## Architecture Overview

```mermaid
flowchart TD
    subgraph GCS["Google Cloud Storage (europe-west2)"]
        Landing["gs://{project}-adventureworks-raw-london/raw/adventureworks/*.csv\n(28 Pipe-Delimited DW Tables)"]
    end

    subgraph Dataflow["Cloud Dataflow Ingestion Engine (Python 3.12)"]
        BeamPipeline["Apache Beam Ingestion Pipeline\n• Pipe-delimited parsing & schema validation\n• Ingestion audit columns (_ingested_at, _source_file)\n• Dead-Letter Queue (DLQ) for malformed rows"]
    end

    subgraph BigQuery["BigQuery Medallion Lakehouse (europe-west2)"]
        subgraph Bronze["🥉 Bronze Layer (adventureworks_bronze)"]
            RawTables["28 Raw Tables (1:1 with source)\nExact high-fidelity snapshot"]
        end

        subgraph Silver["🥈 Silver Layer (adventureworks_silver - dbt models)"]
            CleanDims["Conformed Dims & Cleaned Facts\n• Strictly typed (DATE, NUMERIC, INT64, BOOL)\n• Partitioned on OrderDate / Transaction Date\n• Clustered on Keys (CustomerKey, ProductKey, etc.)\n• Deduplication & surrogate key handling"]
        end

        subgraph Gold["🥇 Gold Layer (adventureworks_gold - dbt marts)"]
            M1["📊 mart_sales_executive_overview\n(Omni-channel revenue, profit margins, growth)"]
            M2["👥 mart_customer_360_rfm\n(Customer RFM segmentation, LTV, repeat rates)"]
            M3["📦 mart_inventory_supply_chain\n(Stockout risk, reorder alerts, inventory valuation)"]
            M4["💼 mart_sales_rep_quota_performance\n(Quota attainment %, rep commission, rankings)"]
            M5["💰 mart_finance_pnl_summary\n(Actual vs Budget variance, OPEX rollups)"]
        end
    end

    Landing --> BeamPipeline
    BeamPipeline --> RawTables
    RawTables -->|dbt run (Silver Models)| CleanDims
    CleanDims -->|dbt run (Gold Marts)| M1 & M2 & M3 & M4 & M5
```

---

## Medallion Layer Specifications

| Layer | Dataset | Description & Best Practices |
| :--- | :--- | :--- |
| **🥉 Bronze** | `adventureworks_bronze` | **Raw Ingestion**: Full fidelity snapshot of all 28 tables (`DimCustomer`, `FactInternetSales`, `FactProductInventory`, etc.). Preserves raw strings and null values with audit columns (`_ingested_at`, `_source_file`, `_raw_row_id`). |
| **🥈 Silver** | `adventureworks_silver` | **Cleansed & Conformed**: Data types cast to strict native BigQuery types (`NUMERIC`, `TIMESTAMP`, `DATE`), standard surrogate key handling (`-1` for unknown), deduplication, and data hygiene.<br>• **Partitioning**: Partition facts by transaction date (`order_date` / `movement_date`).<br>• **Clustering**: Cluster on high-cardinality keys (`customer_key`, `product_key`, `sales_territory_key`). |
| **🥇 Gold** | `adventureworks_gold` | **Business Data Marts**: Ready for Looker, BI, and ML consumption. Curated dimensional models, unified omni-channel sales (Internet + Reseller), and analytical aggregates. |

---

## Gold Analytical Marts & Persona Metrics

1. **Executive & Commercial Leadership (`mart_sales_executive_overview`)**
   - **Metrics**: Gross Revenue, Net Revenue, Cost of Goods Sold (COGS), Gross Profit, Gross Margin %, Average Order Value (AOV).
   - **Dimensions**: Unified Omni-channel (Internet + Reseller), Sales Territory, Country, Product Category & Subcategory, Year/Month.
2. **Marketing & Customer Analytics (`mart_customer_360_rfm`)**
   - **Metrics**: RFM Scoring (Recency, Frequency, Monetary), Segment Assignment (*Champions, Loyal, At Risk, Hibernating, New*), Customer Lifetime Value (LTV), Purchase Intervals.
   - **Dimensions**: Demographics (Income tier, Education, Occupation, Homeowner, Commute distance, Geography).
3. **Supply Chain & Inventory Management (`mart_inventory_supply_chain`)**
   - **Metrics**: Ending Inventory Balance, Inventory Valuation ($), Stockout Warning, Reorder Point trigger boolean.
   - **Dimensions**: Product Category, Subcategory, SKU, Daily Timeline.
4. **Sales Reps & Channel Partners (`mart_sales_rep_quota_performance`)**
   - **Metrics**: Quarterly Quota Target ($), Actual Closed Reseller Sales ($), Quota Attainment %, Quota Variance.
   - **Dimensions**: Sales Representative, Department, Year/Quarter, Performance Bracket.
5. **Finance & FP&A (`mart_finance_pnl_summary`)**
   - **Metrics**: General Ledger amounts, Variance between Actual vs Budget/Forecast.
   - **Dimensions**: Account Description, Account Type (Revenue, Expense, Asset, Liability), Department Group, Organization.

---

## Quickstart Guide

### 1. Prerequisites
- Google Cloud SDK (`gcloud` CLI) authenticated to your project.
- Python 3.12+ installed.

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/SadeeqAkintola/adventure-works-medallion-project.git
cd adventure-works-medallion-project

# Create Python 3.12 virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. End-to-End Execution

#### Step 1: Provision GCP Resources (in `europe-west2`)
```bash
python scripts/01_setup_gcp_resources.py --project-id=idyllic-theater-agentic-ai --location=europe-west2
```

#### Step 2: Upload Raw CSVs to Cloud Storage
```bash
python scripts/02_upload_raw_to_gcs.py --project-id=idyllic-theater-agentic-ai
```

#### Step 3: Run Dataflow Ingestion Pipeline (GCS $\rightarrow$ Bronze)
```bash
# For local / testing with DirectRunner:
python scripts/03_run_dataflow_migration.py --project-id=idyllic-theater-agentic-ai --runner=DirectRunner

# For distributed execution on Google Cloud Dataflow:
python scripts/03_run_dataflow_migration.py --project-id=idyllic-theater-agentic-ai --runner=DataflowRunner
```

#### Step 4: Execute dbt Transformations & Data Quality Tests
```bash
./scripts/04_run_dbt_transformations.sh
```

#### Step 5: Validate Medallion Lakehouse State
```bash
python scripts/validate_medallion.py --project-id=idyllic-theater-agentic-ai
```

---

## Repository Structure

```
adventure-works-medallion-project/
├── .github/
│   └── workflows/ci.yml             # GitHub Actions CI for dbt and schemas
├── dataflow/                        # Apache Beam Ingestion Engine (Python 3.12)
│   ├── config/
│   │   └── table_schemas.py         # Explicit BigQuery schemas for all 28 tables
│   ├── pipeline.py                  # Main Beam pipeline (GCS -> Bronze BigQuery)
│   └── requirements.txt
├── dbt_adventureworks/              # dbt-bigquery Project
│   ├── dbt_project.yml
│   ├── profiles.yml                 # BigQuery europe-west2 profile
│   ├── models/
│   │   ├── staging/sources.yml      # Bronze source declarations
│   │   ├── silver/                  # Cleaned & conformed models (dim_*, fact_*)
│   │   ├── gold/                    # Persona analytical marts (mart_*)
│   │   └── schema_tests.yml         # Integrity and uniqueness assertions
├── scripts/
│   ├── 01_setup_gcp_resources.py    # Provision GCS bucket & BigQuery datasets
│   ├── 02_upload_raw_to_gcs.py      # Multi-threaded GCS upload
│   ├── 03_run_dataflow_migration.py # Dataflow runner
│   ├── 04_run_dbt_transformations.sh# dbt execute & test
│   ├── extract_schemas.py           # SQL DDL to BigQuery schema extractor
│   └── validate_medallion.py        # Lakehouse reconciliation report
├── docs/
│   ├── architecture.md              # Architecture deep-dive
│   └── data_dictionary.md           # Schema & field catalog
├── requirements.txt
└── README.md
```

---

## Author
- **Sadeeq Akintola** - [GitHub Profile](https://github.com/SadeeqAkintola)
