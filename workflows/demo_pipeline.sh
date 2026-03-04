#!/bin/bash

# Configuration
DATASET_DIR="dataset/demo_calls"
OUTPUT_DIR="outputs/accounts"
LOG_FILE="logs/pipeline_runs.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] demo_pipeline started" | tee -a $LOG_FILE

# Ensure directories exist
mkdir -p $OUTPUT_DIR
mkdir -p logs

for file in $DATASET_DIR/*.txt; do
    if [ ! -f "$file" ]; then
        continue
    fi
    filename=$(basename -- "$file")
    
    # Extract ID (e.g., demo_001.txt -> 001, account_001)
    # Using python to parse to be robust
    account_num=$(echo $filename | grep -o -E '[0-9]+')
    account_id="account_$account_num"
    
    echo "Processing Demo for $account_id..."
    
    # Setup directories
    v1_dir="$OUTPUT_DIR/$account_id/v1"
    mkdir -p "$v1_dir"
    
    # Step 1: Extract Data -> Memo v1
    memo_path="$v1_dir/memo.json"
    python3 scripts/extract_data.py --transcript "$file" --output "$memo_path" --account_id "$account_id" --stage demo
    
    # Step 2: Generate Agent Spec v1
    agent_path="$v1_dir/agent_spec.json"
    python3 scripts/generate_agent.py --memo "$memo_path" --output "$agent_path" --version v1
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $account_id v1 created" | tee -a $LOG_FILE
done

echo "Demo pipeline complete!"
