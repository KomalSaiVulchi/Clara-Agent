#!/bin/bash

# Configuration
DATASET_DIR="dataset/onboarding_calls"
OUTPUT_DIR="outputs/accounts"
LOG_FILE="logs/pipeline_runs.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] onboarding_pipeline started" | tee -a $LOG_FILE

# Ensure directories exist
mkdir -p $OUTPUT_DIR
mkdir -p logs

for file in $DATASET_DIR/*.txt; do
    if [ ! -f "$file" ]; then
        continue
    fi
    filename=$(basename -- "$file")
    
    # Extract ID
    account_num=$(echo $filename | grep -o -E '[0-9]+')
    account_id="account_$account_num"
    
    echo "Processing Onboarding for $account_id..."
    
    # Setup directories
    account_dir="$OUTPUT_DIR/$account_id"
    v1_memo="$account_dir/v1/memo.json"
    v2_dir="$account_dir/v2"
    mkdir -p "$v2_dir"
    
    if [ ! -f "$v1_memo" ]; then
         echo "Warning: No v1 memo found for $account_id. Skipping."
         continue
    fi
    
    # Step 1: Extract Updated Data
    temp_updates="outputs/temp_updates_${account_id}.json"
    python3 scripts/extract_data.py --transcript "$file" --output "$temp_updates" --account_id "$account_id" --stage onboarding
    
    # Step 2: Merge Updates -> Memo v2
    v2_memo="$v2_dir/memo.json"
    python3 scripts/merge_updates.py --v1_memo "$v1_memo" --extracted_updates "$temp_updates" --output "$v2_memo"
    
    # Step 3: Generate Agent Spec v2
    agent_path="$v2_dir/agent_spec.json"
    python3 scripts/generate_agent.py --memo "$v2_memo" --output "$agent_path" --version v2
    
    # Step 4: Generate Changelog
    changelog_path="$account_dir/changelog.json"
    python3 scripts/create_changelog.py --v1_memo "$v1_memo" --v2_memo "$v2_memo" --account_id "$account_id" --output "$changelog_path"
    
    # Cleanup temp
    rm "$temp_updates"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $account_id v2 created" | tee -a $LOG_FILE
done

echo "Generating HTML Viewer..."
python3 scripts/generate_viewer.py

echo "Onboarding pipeline complete!"
