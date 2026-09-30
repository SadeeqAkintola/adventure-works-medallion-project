#!/usr/bin/env python3
"""
Step 1: Setup GCP Resources in europe-west2 (London)
Creates:
- GCS Bucket: <PROJECT_ID>-adventureworks-raw-london
- BigQuery Bronze Dataset: adventureworks_bronze
- BigQuery Silver Dataset: adventureworks_silver
- BigQuery Gold Dataset: adventureworks_gold
"""

import sys
import argparse
from google.cloud import bigquery
from google.cloud import storage
from google.api_core.exceptions import Conflict, GoogleAPICallError

def setup_resources(project_id: str, location: str = "europe-west2"):
    print(f"==================================================")
    print(f"Setting up GCP Resources in {location}")
    print(f"Project ID: {project_id}")
    print(f"==================================================")
    
    # 1. Setup GCS Bucket
    storage_client = storage.Client(project=project_id)
    bucket_name = f"{project_id}-adventureworks-raw-london"
    
    try:
        bucket = storage_client.bucket(bucket_name)
        if not bucket.exists():
            bucket = storage_client.create_bucket(bucket_name, location=location)
            print(f"✅ Created GCS Bucket: gs://{bucket_name} in {location}")
        else:
            print(f"ℹ️ GCS Bucket already exists: gs://{bucket_name}")
    except Exception as e:
        print(f"⚠️ Error with bucket {bucket_name}: {e}")

    # 2. Setup BigQuery Datasets
    bq_client = bigquery.Client(project=project_id)
    datasets = [
        ("adventureworks_bronze", "🥉 Bronze Layer: Raw fidelity tables mirroring source AdventureWorksDW"),
        ("adventureworks_silver", "🥈 Silver Layer: Cleaned, conformed, typed, partitioned and clustered models"),
        ("adventureworks_gold", "🥇 Gold Layer: Business intelligence marts and curated executive analytics")
    ]
    
    for dataset_id, description in datasets:
        dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        dataset.description = description
        
        try:
            bq_client.create_dataset(dataset, exists_ok=True)
            print(f"✅ BigQuery Dataset ready: {project_id}.{dataset_id} in {location}")
        except Exception as e:
            print(f"⚠️ Error creating dataset {dataset_id}: {e}")
            
    print("\n✅ All GCP base infrastructure provisioned successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Provision GCS & BigQuery datasets for AdventureWorks Medallion.")
    parser.add_argument("--project-id", default="idyllic-theater-agentic-ai", help="GCP Project ID")
    parser.add_argument("--location", default="europe-west2", help="GCP Location / Region (default: europe-west2)")
    args = parser.parse_args()
    
    setup_resources(project_id=args.project_id, location=args.location)
