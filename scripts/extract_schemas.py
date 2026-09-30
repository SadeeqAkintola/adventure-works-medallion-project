#!/usr/bin/env python3
"""
Extract BigQuery Table Schemas from instawdbdw.sql
Parses CREATE TABLE statements and maps SQL Server types to BigQuery types.
"""
import re
import json
from pathlib import Path

TYPE_MAP = {
    'int': 'INTEGER',
    'smallint': 'INTEGER',
    'tinyint': 'INTEGER',
    'bigint': 'INTEGER',
    'bit': 'BOOLEAN',
    'decimal': 'NUMERIC',
    'numeric': 'NUMERIC',
    'money': 'NUMERIC',
    'smallmoney': 'NUMERIC',
    'float': 'FLOAT',
    'real': 'FLOAT',
    'datetime': 'TIMESTAMP',
    'smalldatetime': 'TIMESTAMP',
    'date': 'DATE',
    'time': 'TIME',
    'nvarchar': 'STRING',
    'varchar': 'STRING',
    'nchar': 'STRING',
    'char': 'STRING',
    'text': 'STRING',
    'ntext': 'STRING',
    'xml': 'STRING',
    'sysname': 'STRING',
    'varbinary': 'BYTES',
    'image': 'BYTES',
    'uniqueidentifier': 'STRING',
}

def parse_sql_ddl(sql_path: Path):
    content = sql_path.read_text(encoding='utf-8', errors='ignore')
    
    # Regex to find CREATE TABLE blocks
    create_table_regex = re.compile(
        r'CREATE\s+TABLE\s+(?:\[dbo\]\.)?\[?(\w+)\]?\s*\((.*?)\)\s*(?:ON\s+\[PRIMARY\])?(?:\s*WITH\s*\(.*?\))?;',
        re.DOTALL | re.IGNORECASE
    )
    
    # Also find BULK INSERT mappings
    bulk_insert_regex = re.compile(
        r'BULK\s+INSERT\s+(?:\[dbo\]\.)?\[?(\w+)\]?\s+FROM\s+\'[^\']*?(\w+\.csv)\'',
        re.IGNORECASE
    )
    
    bulk_mappings = dict(bulk_insert_regex.findall(content))
    tables = {}
    
    for match in create_table_regex.finditer(content):
        table_name = match.group(1)
        body = match.group(2)
        
        columns = []
        for line in body.split('\n'):
            line = line.strip()
            if not line or line.startswith('--') or line.startswith('/*') or line.startswith('CONSTRAINT') or line.startswith('PRIMARY KEY'):
                continue
            
            # Match column definition: [ColName] [type](params) NULL/NOT NULL
            col_match = re.match(r'\[?(\w+)\]?\s+\[?(\w+)\]?(?:\s*\([^)]*\))?\s*(IDENTITY\s*\([^)]*\))?\s*(NOT\s+NULL|NULL)?', line, re.IGNORECASE)
            if col_match:
                col_name = col_match.group(1)
                sql_type = col_match.group(2).lower()
                is_nullable = False if col_match.group(4) and 'NOT' in col_match.group(4).upper() else True
                
                # Check for reserved / keyword names
                bq_type = TYPE_MAP.get(sql_type, 'STRING')
                columns.append({
                    'name': col_name,
                    'type': bq_type,
                    'mode': 'NULLABLE', # BigQuery raw bronze ingestion is best NULLABLE to avoid dropouts
                    'raw_sql_type': sql_type
                })
        
        if columns:
            tables[table_name] = {
                'table_name': table_name,
                'csv_file': bulk_mappings.get(table_name, f"{table_name}.csv"),
                'columns': columns
            }
            
    return tables

if __name__ == '__main__':
    project_root = Path(__file__).parent.parent
    sql_file = project_root / 'AdventureWorksDW-data-warehouse-install-script' / 'instawdbdw.sql'
    tables = parse_sql_ddl(sql_file)
    print(f"Extracted {len(tables)} tables from SQL DDL:")
    for name, data in tables.items():
        print(f"  - {name}: {len(data['columns'])} columns (CSV: {data['csv_file']})")
    
    out_file = project_root / 'scripts' / 'schemas.json'
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(tables, indent=2))
    print(f"\nSaved schemas to {out_file}")
