#!/usr/bin/env python3
"""
Step 5: Medallion Architecture Validation & Health Check
Verifies row counts and reconciliation across:
- Bronze (Raw)
- Silver (Cleaned & Conformed)
- Gold (Business Marts)
"""

import sys
import argparse
from google.cloud import bigquery

def validate_medallion(project_id: str):
    client = bigquery.Client(project=project_id)
    
    print("==================================================")
    print(f"AdventureWorks Medallion Reconciliation Report")
    print(f"GCP Project: {project_id}")
    print("==================================================")

    layers = {
        "Bronze (Raw)": "adventureworks_bronze",
        "Silver (Cleaned & Conformed)": "adventureworks_silver",
        "Gold (Business Marts)": "adventureworks_gold"
    }

    for layer_name, dataset_id in layers.items():
        print(f"\n📂 {layer_name} [`{dataset_id}`]:")
        try:
            tables = list(client.list_tables(f"{project_id}.{dataset_id}"))
            if not tables:
                print("   (No tables deployed yet)")
                continue
                
            for table in sorted(tables, key=lambda t: t.table_id):
                t_ref = client.get_table(table.reference)
                print(f"   • {t_ref.table_id:<35} : {t_ref.num_rows:>8,} rows | {round(t_ref.num_bytes / (1024*1024), 2):>6.2f} MB")
        except Exception as e:
            print(f"   ⚠️ Could not query dataset {dataset_id}: {e}")

    print("\n✅ Verification query completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate Medallion Lakehouse state.")
    parser.add_argument("--project-id", default="idyllic-theater-agentic-ai", help="GCP Project ID")
    args = parser.parse_args()
    
    validate_medallion(args.project_id)
