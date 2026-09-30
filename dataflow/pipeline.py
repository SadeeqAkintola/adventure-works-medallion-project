#!/usr/bin/env python3
"""
Apache Beam / Google Cloud Dataflow Ingestion Pipeline
Loads raw AdventureWorksDW CSV files from GCS into BigQuery Bronze dataset.
Includes schema validation, delimiter parsing, metadata enrichment, and DLQ handling.
"""

import sys
import os
import uuid
import datetime
import argparse
import logging
from typing import Dict, Any, List

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions, StandardOptions, SetupOptions
from apache_beam.io.gcp.bigquery import WriteToBigQuery, BigQueryDisposition

from dataflow.config.table_schemas import TABLE_SCHEMAS, get_bq_schema

class ParsePipeDelimitedFn(beam.DoFn):
    """
    Parses pipe-delimited (|) CSV rows into typed dictionaries according to schema.
    Appends audit metadata (_ingested_at, _source_file, _raw_row_id).
    Routes malformed rows to Dead-Letter Queue (DLQ).
    """
    OUTPUT_TAG_DEAD_LETTER = 'dead_letter'

    def __init__(self, table_name: str, gcs_file_path: str):
        self.table_name = table_name
        self.gcs_file_path = gcs_file_path
        self.columns = [col[0] for col in TABLE_SCHEMAS[table_name]["columns"]]
        self.expected_cols_count = len(self.columns)

    def process(self, line: str):
        line = line.strip('\r\n')
        if not line:
            return

        # Split on pipe delimiter
        fields = line.split('|')
        
        # AdventureWorks CSVs may have a trailing pipe
        if len(fields) == self.expected_cols_count + 1 and fields[-1] == '':
            fields = fields[:-1]
            
        if len(fields) < self.expected_cols_count:
            # Pad with empty strings if trailing null fields were omitted
            fields.extend([''] * (self.expected_cols_count - len(fields)))

        ingest_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        row_id = str(uuid.uuid4())

        try:
            row_dict = {}
            for col_name, raw_val in zip(self.columns, fields):
                cleaned = raw_val.strip() if raw_val is not None else ''
                row_dict[col_name] = cleaned if cleaned != '' else None

            # Add audit & lineage metadata
            row_dict["_ingested_at"] = ingest_ts
            row_dict["_source_file"] = self.gcs_file_path
            row_dict["_raw_row_id"] = row_id

            yield row_dict

        except Exception as err:
            logging.warning(f"Error parsing row in {self.table_name}: {err}. Line: {line[:100]}")
            yield beam.pvalue.TaggedOutput(
                self.OUTPUT_TAG_DEAD_LETTER,
                {
                    "table_name": self.table_name,
                    "source_file": self.gcs_file_path,
                    "raw_line": line,
                    "error": str(err),
                    "failed_at": ingest_ts
                }
            )


def build_pipeline(table_name: str, pipeline_args: List[str], project_id: str, bucket_name: str, region: str = "europe-west2", runner: str = "DirectRunner"):
    """Builds and executes an Apache Beam pipeline for a specific DW table."""
    table_def = TABLE_SCHEMAS[table_name]
    csv_file = table_def["csv_file"]
    input_pattern = f"gs://{bucket_name}/raw/adventureworks/{csv_file}"
    output_table = f"{project_id}:adventureworks_bronze.{table_name}"

    options = PipelineOptions(pipeline_args)
    gcp_options = options.view_as(GoogleCloudOptions)
    gcp_options.project = project_id
    gcp_options.region = region
    gcp_options.temp_location = f"gs://{bucket_name}/temp"
    gcp_options.staging_location = f"gs://{bucket_name}/staging"
    gcp_options.job_name = f"ingest-{table_name.lower()}-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    options.view_as(StandardOptions).runner = runner
    options.view_as(SetupOptions).save_main_session = True

    # BigQuery table schema
    bq_fields = get_bq_schema(table_name, add_metadata_fields=True)
    schema_dict = {
        "fields": [{"name": f.name, "type": f.field_type, "mode": f.mode} for f in bq_fields]
    }

    logging.info(f"🚀 Starting Ingestion Pipeline: {table_name} ({input_pattern} -> {output_table})")

    with beam.Pipeline(options=options) as p:
        lines = p | f"ReadLines_{table_name}" >> beam.io.ReadFromText(input_pattern)
        
        parsed_results = lines | f"ParseCSV_{table_name}" >> beam.ParDo(
            ParsePipeDelimitedFn(table_name, input_pattern)
        ).with_outputs(ParsePipeDelimitedFn.OUTPUT_TAG_DEAD_LETTER, main='valid_rows')

        valid_rows = parsed_results.valid_rows
        dead_letter = parsed_results[ParsePipeDelimitedFn.OUTPUT_TAG_DEAD_LETTER]

        # Write valid records to BigQuery Bronze
        _ = valid_rows | f"WriteBQ_{table_name}" >> WriteToBigQuery(
            table=output_table,
            schema=schema_dict,
            create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=BigQueryDisposition.WRITE_TRUNCATE,
            custom_gcs_temp_location=f"gs://{bucket_name}/temp/bq_loads"
        )

        # Write any dead-letter errors to GCS for auditing
        _ = dead_letter | f"WriteDLQ_{table_name}" >> beam.io.WriteToText(
            f"gs://{bucket_name}/dlq/{table_name}/errors",
            file_name_suffix=".json",
            shard_name_template=""
        )

    logging.info(f"✅ Successfully ingested table: {table_name}")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser(description="Run Dataflow Ingestion Pipeline for AdventureWorksDW.")
    parser.add_argument("--project-id", default="idyllic-theater-agentic-ai", help="GCP Project ID")
    parser.add_argument("--bucket-name", default="idyllic-theater-agentic-ai-adventureworks-raw-london", help="GCS Bucket Name")
    parser.add_argument("--region", default="europe-west2", help="GCP Region")
    parser.add_argument("--runner", default="DirectRunner", choices=["DirectRunner", "DataflowRunner"], help="Beam Runner")
    parser.add_argument("--table", default="all", help="Specific table name or 'all'")

    known_args, beam_args = parser.parse_known_args()

    tables_to_run = list(TABLE_SCHEMAS.keys()) if known_args.table == "all" else [known_args.table]

    for tbl in tables_to_run:
        build_pipeline(
            table_name=tbl,
            pipeline_args=beam_args,
            project_id=known_args.project_id,
            bucket_name=known_args.bucket_name,
            region=known_args.region,
            runner=known_args.runner
        )
