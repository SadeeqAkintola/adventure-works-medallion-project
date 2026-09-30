#!/usr/bin/env python3
"""
Step 2: Fast Parallel Upload of Raw DW CSVs to Google Cloud Storage (GCS)
Location: europe-west2 (London)
Bucket: gs://<PROJECT_ID>-adventureworks-raw-london/raw/
"""

import os
import sys
import glob
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import storage

def upload_single_file(bucket_name: str, local_path: Path, remote_prefix: str, project_id: str) -> dict:
    """Uploads a single file to GCS and returns status."""
    try:
        client = storage.Client(project=project_id)
        bucket = client.bucket(bucket_name)
        blob_path = f"{remote_prefix.rstrip('/')}/{local_path.name}"
        blob = bucket.blob(blob_path)
        
        file_size_mb = local_path.stat().st_size / (1024 * 1024)
        blob.upload_from_filename(str(local_path))
        return {
            "file": local_path.name,
            "size_mb": round(file_size_mb, 2),
            "gcs_uri": f"gs://{bucket_name}/{blob_path}",
            "status": "SUCCESS"
        }
    except Exception as e:
        return {
            "file": local_path.name,
            "status": "ERROR",
            "error": str(e)
        }

def upload_all_files(project_id: str, data_dir: str, remote_prefix: str = "raw/adventureworks", max_workers: int = 8):
    bucket_name = f"{project_id}-adventureworks-raw-london"
    source_path = Path(data_dir)
    
    csv_files = list(source_path.glob("*.csv"))
    if not csv_files:
        print(f"❌ No CSV files found in {data_dir}")
        sys.exit(1)
        
    print(f"==================================================")
    print(f"Uploading {len(csv_files)} DW files to gs://{bucket_name}/{remote_prefix}")
    print(f"==================================================")
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(upload_single_file, bucket_name, f, remote_prefix, project_id): f
            for f in csv_files
        }
        
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            if res["status"] == "SUCCESS":
                print(f"  ✅ Uploaded: {res['file']} ({res['size_mb']} MB) -> {res['gcs_uri']}")
            else:
                print(f"  ❌ Failed: {res['file']} - {res.get('error')}")
                
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    print(f"\n🎉 Successfully uploaded {success_count}/{len(csv_files)} files to Cloud Storage.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload raw CSV files to GCS.")
    parser.add_argument("--project-id", default="idyllic-theater-agentic-ai", help="GCP Project ID")
    default_data_dir = str(Path(__file__).parent.parent / "AdventureWorksDW-data-warehouse-install-script")
    parser.add_argument("--data-dir", default=default_data_dir, help="Path to raw DW directory")
    parser.add_argument("--remote-prefix", default="raw/adventureworks", help="GCS folder prefix")
    parser.add_argument("--workers", type=int, default=8, help="Parallel upload threads")
    
    args = parser.parse_args()
    upload_all_files(project_id=args.project_id, data_dir=args.data_dir, remote_prefix=args.remote_prefix, max_workers=args.workers)
