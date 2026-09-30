#!/usr/bin/env python3
"""
Step 3: Run Dataflow / Apache Beam Migration Pipeline
Executes ingestion of all 28 AdventureWorksDW tables from GCS into BigQuery Bronze dataset.
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_migration(project_id: str, bucket_name: str, region: str = "europe-west2", runner: str = "DirectRunner"):
    print("==================================================")
    print("Executing Dataflow Ingestion Pipeline")
    print(f"Project ID: {project_id}")
    print(f"Bucket: gs://{bucket_name}")
    print(f"Region: {region}")
    print(f"Runner: {runner}")
    print("==================================================")
    
    pipeline_script = Path(__file__).parent.parent / "dataflow" / "pipeline.py"
    
    cmd = [
        sys.executable,
        str(pipeline_script),
        f"--project-id={project_id}",
        f"--bucket-name={bucket_name}",
        f"--region={region}",
        f"--runner={runner}",
        "--table=all"
    ]
    
    print(f"Running command: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n🎉 Dataflow Bronze ingestion completed successfully!")
    else:
        print(f"\n❌ Migration failed with exit code: {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Dataflow Migration for AdventureWorksDW.")
    parser.add_argument("--project-id", default="idyllic-theater-agentic-ai", help="GCP Project ID")
    parser.add_argument("--bucket-name", default="idyllic-theater-agentic-ai-adventureworks-raw-london", help="GCS Bucket Name")
    parser.add_argument("--region", default="europe-west2", help="GCP Region")
    parser.add_argument("--runner", default="DirectRunner", choices=["DirectRunner", "DataflowRunner"], help="Beam Runner")
    
    args = parser.parse_args()
    run_migration(project_id=args.project_id, bucket_name=args.bucket_name, region=args.region, runner=args.runner)
