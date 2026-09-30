#!/usr/bin/env bash
# Step 4: Run dbt Transformations & Data Quality Tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DBT_DIR="$PROJECT_ROOT/dbt_adventureworks"

echo "=================================================="
echo "Running dbt Medallion Transformations (BigQuery)"
echo "Target Directory: $DBT_DIR"
echo "=================================================="

# Activate virtualenv if available
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

cd "$DBT_DIR"

echo "1. Checking dbt connection..."
dbt debug --profiles-dir .

echo -e "\n2. Compiling models..."
dbt compile --profiles-dir .

echo -e "\n3. Executing Silver & Gold Transformations..."
dbt run --profiles-dir .

echo -e "\n4. Running Data Quality Assertions & Tests..."
dbt test --profiles-dir .

echo -e "\n🎉 Medallion transformations and tests completed successfully!"
