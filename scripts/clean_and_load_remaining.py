#!/usr/bin/env python3
"""
Clean binary ASCII 0 characters from DimProduct.csv and DimEmployee.csv
and load them into BigQuery Bronze.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.cloud import bigquery, storage
from dataflow.config.table_schemas import TABLE_SCHEMAS

def clean_and_load_table(project_id: str, bucket_name: str, table_name: str, location: str = "europe-west2"):
    bq_client = bigquery.Client(project=project_id, location=location)
    storage_client = storage.Client(project=project_id)
    
    table_info = TABLE_SCHEMAS[table_name]
    csv_file = table_info["csv_file"]
    local_csv_path = Path(__file__).parent.parent / "AdventureWorksDW-data-warehouse-install-script" / csv_file
    cleaned_csv_path = Path(__file__).parent.parent / "AdventureWorksDW-data-warehouse-install-script" / f"cleaned_{csv_file}"
    
    print(f"Cleaning binary null bytes in {csv_file}...")
    with open(local_csv_path, "rb") as fin, open(cleaned_csv_path, "wb") as fout:
        content = fin.read()
        # Replace null byte (\x00) with empty string
        cleaned_content = content.replace(b"\x00", b"")
        fout.write(cleaned_content)
        
    print(f"Uploading cleaned_{csv_file} to GCS...")
    bucket = storage_client.bucket(bucket_name)
    gcs_blob_name = f"raw/adventureworks/{csv_file}"
    blob = bucket.blob(gcs_blob_name)
    blob.upload_from_filename(str(cleaned_csv_path))
    
    # Remove temporary cleaned file
    cleaned_csv_path.unlink()
    
    print(f"Loading {table_name} into BigQuery Bronze...")
    gcs_uri = f"gs://{bucket_name}/{gcs_blob_name}"
    table_ref = f"{project_id}.adventureworks_bronze.{table_name}"
    
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
    
    load_job = bq_client.load_table_from_uri(gcs_uri, table_ref, job_config=job_config)
    load_job.result()
    
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
    print(f"✅ Successfully loaded {table_name} ({dest_table.num_rows:,} rows) into Bronze!")

if __name__ == "__main__":
    project_id = "idyllic-theater-agentic-ai"
    bucket_name = "idyllic-theater-agentic-ai-adventureworks-raw-london"
    
    clean_and_load_table(project_id, bucket_name, "DimProduct")
    clean_and_load_table(project_id, bucket_name, "DimEmployee")
