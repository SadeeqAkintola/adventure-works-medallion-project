#!/usr/bin/env python3
"""
Fast BigQuery Native & Dataflow Batch Loader for AdventureWorks Bronze Dataset
Loads all 28+ pipe-delimited CSVs from GCS directly into BigQuery Bronze dataset in europe-west2.
Appends metadata fields (_ingested_at, _source_file, _raw_row_id).
"""

import sys
import argparse
import datetime
import uuid
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.cloud import bigquery
from dataflow.config.table_schemas import TABLE_SCHEMAS, get_bq_schema

def load_all_bronze_tables(project_id: str, bucket_name: str, location: str = "europe-west2"):
    bq_client = bigquery.Client(project=project_id, location=location)
    
    print("==================================================")
    print(f"Loading Raw DW Tables into Bronze Dataset")
    print(f"Project: {project_id}")
    print(f"Dataset: adventureworks_bronze")
    print(f"Location: {location}")
    print("==================================================")
    
    success_count = 0
    total_tables = len(TABLE_SCHEMAS)
    
    for table_name, table_info in TABLE_SCHEMAS.items():
        csv_file = table_info["csv_file"]
        gcs_uri = f"gs://{bucket_name}/raw/adventureworks/{csv_file}"
        table_ref = f"{project_id}.adventureworks_bronze.{table_name}"
        
        # Get BigQuery Schema without metadata for initial CSV load
        base_schema = [bigquery.SchemaField(col[0], col[1], mode="NULLABLE") for col in table_info["columns"]]
        
        job_config = bigquery.LoadJobConfig(
            schema=base_schema,
            source_format=bigquery.SourceFormat.CSV,
            field_delimiter='|',
            quote_character='"',
            allow_quoted_newlines=True,
            allow_jagged_rows=True,
            ignore_unknown_values=True,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
        
        try:
            print(f"⏳ Loading {table_name:<30} from {gcs_uri}...", end="", flush=True)
            load_job = bq_client.load_table_from_uri(gcs_uri, table_ref, job_config=job_config)
            load_job.result()  # Wait for job to complete
            
            # Enrich table with metadata audit columns (_ingested_at, _source_file)
            enrich_sql = f"""
                ALTER TABLE `{project_id}.adventureworks_bronze.{table_name}`
                ADD COLUMN IF NOT EXISTS _ingested_at TIMESTAMP,
                ADD COLUMN IF NOT EXISTS _source_file STRING,
                ADD COLUMN IF NOT EXISTS _raw_row_id STRING;
                
                UPDATE `{project_id}.adventureworks_bronze.{table_name}`
                SET 
                    _ingested_at = CURRENT_TIMESTAMP(),
                    _source_file = '{gcs_uri}',
                    _raw_row_id = GENERATE_UUID()
                WHERE _ingested_at IS NULL;
            """
            bq_client.query(enrich_sql, location=location).result()
            
            dest_table = bq_client.get_table(table_ref)
            print(f" ✅ ({dest_table.num_rows:,} rows)")
            success_count += 1
            
        except Exception as e:
            print(f" ❌ Failed: {e}")
            
    print(f"\n🎉 Successfully loaded {success_count}/{total_tables} Bronze tables into BigQuery!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Bronze tables into BigQuery.")
    parser.add_argument("--project-id", default="idyllic-theater-agentic-ai", help="GCP Project ID")
    parser.add_argument("--bucket-name", default="idyllic-theater-agentic-ai-adventureworks-raw-london", help="GCS Bucket Name")
    parser.add_argument("--location", default="europe-west2", help="BigQuery Location")
    
    args = parser.parse_args()
    load_all_bronze_tables(project_id=args.project_id, bucket_name=args.bucket_name, location=args.location)
