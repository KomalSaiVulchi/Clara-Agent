import os
import json
import argparse
import logging
import copy

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d')

def update_dict_recursively(base, updates):
    """Deep merge of dictionaries"""
    for k, v in updates.items():
        if isinstance(v, dict) and k in base and isinstance(base[k], dict):
            base[k] = update_dict_recursively(base[k], v)
        elif isinstance(v, list) and k in base and isinstance(base[k], list):
            # For lists like services supported, we append unique items or just replace if complex
            for item in v:
                if item not in base[k]:
                    base[k].append(item)
        else:
            base[k] = v
    return base

def main():
    parser = argparse.ArgumentParser(description="Merge extracted onboarding data into v1 memo to create v2 memo.")
    parser.add_argument("--v1_memo", required=True, help="Path to v1 memo JSON")
    parser.add_argument("--extracted_updates", required=True, help="Path to extracted JSON from onboarding")
    parser.add_argument("--output", required=True, help="Path to save v2 memo JSON")
    
    args = parser.parse_args()
    
    with open(args.v1_memo, "r") as f:
        v1_memo = json.load(f)
        
    with open(args.extracted_updates, "r") as f:
        updates = json.load(f)
        
    # Create v2 by deep merging
    v2_memo = copy.deepcopy(v1_memo)
    v2_memo = update_dict_recursively(v2_memo, updates)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    with open(args.output, "w") as f:
        json.dump(v2_memo, f, indent=4)
        
    logging.info(f"v2 memo created and saved to {args.output}")

if __name__ == "__main__":
    main()
