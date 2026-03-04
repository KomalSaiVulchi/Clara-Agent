import os
import json
import argparse
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d')

def generate_changelog(v1: Dict[str, Any], v2: Dict[str, Any], account_id: str) -> Dict[str, Any]:
    changes = []
    
    def compare_dicts(d1, d2, path=""):
        for k in set(d1.keys()).union(set(d2.keys())):
            k_path = f"{path}.{k}" if path else k
            v1_val = d1.get(k)
            v2_val = d2.get(k)
            
            if v1_val == v2_val:
                continue
                
            if isinstance(v1_val, dict) and isinstance(v2_val, dict):
                compare_dicts(v1_val, v2_val, k_path)
            elif isinstance(v1_val, list) and isinstance(v2_val, list):
                # Simple list comparison
                added = set(v2_val) - set(v1_val)
                removed = set(v1_val) - set(v2_val)
                if added:
                    changes.append(f"{k_path} added: {', '.join(map(str, added))}")
                if removed:
                    changes.append(f"{k_path} removed: {', '.join(map(str, removed))}")
            else:
                changes.append(f"{k_path} updated from '{v1_val}' to '{v2_val}'")
                
    compare_dicts(v1, v2)
    
    return {
        "account_id": account_id,
        "version_update": "v1_to_v2",
        "changes": changes
    }

def main():
    parser = argparse.ArgumentParser(description="Generate changelog from v1 and v2 memos.")
    parser.add_argument("--v1_memo", required=True, help="Path to v1 memo JSON")
    parser.add_argument("--v2_memo", required=True, help="Path to v2 memo JSON")
    parser.add_argument("--account_id", required=True, help="Account ID")
    parser.add_argument("--output", required=True, help="Path to save changelog JSON")
    
    args = parser.parse_args()
    
    with open(args.v1_memo, "r") as f:
        v1_memo = json.load(f)
        
    with open(args.v2_memo, "r") as f:
        v2_memo = json.load(f)
        
    changelog = generate_changelog(v1_memo, v2_memo, args.account_id)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    with open(args.output, "w") as f:
        json.dump(changelog, f, indent=4)
        
    logging.info(f"Changelog generated for {args.account_id}")

if __name__ == "__main__":
    main()
