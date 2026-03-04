import os
import json
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d')

SYSTEM_PROMPT_TEMPLATE = """You are Clara, an AI receptionist for {company_name}.

Your job is to handle inbound service calls.

Follow these rules:

BUSINESS HOURS FLOW
1 greet caller
2 ask purpose of call
3 collect name and phone
4 determine emergency or non emergency
5 transfer call to appropriate destination
6 if transfer fails apologize and take message
7 ask if anything else is needed
8 close politely

AFTER HOURS FLOW
1 greet caller
2 ask reason for call
3 confirm emergency
4 if emergency collect name phone address immediately
5 attempt transfer
6 if transfer fails assure follow up
7 if non emergency collect service request
8 confirm follow up during business hours
9 ask if anything else
10 close politely
"""

def generate_agent_spec(memo: dict, version: str) -> dict:
    company_name = memo.get("company_name", "the company")
    
    bh_obj = memo.get("business_hours", {})
    if isinstance(bh_obj, dict):
        hours_str = f"{bh_obj.get('days', '')} {bh_obj.get('start', '')}-{bh_obj.get('end', '')} {bh_obj.get('timezone', '')}".strip()
    else:
        hours_str = str(bh_obj)

    spec = {
        "agent_name": f"Clara - {company_name}",
        "voice_style": "professional friendly",
        "version": version,
        "system_prompt": SYSTEM_PROMPT_TEMPLATE.replace("{company_name}", company_name),
        "key_variables": {
            "timezone": bh_obj.get("timezone", "") if isinstance(bh_obj, dict) else "",
            "business_hours": hours_str,
            "office_address": memo.get("office_address", "") or ""
        },
        "call_transfer_protocol": json.dumps(memo.get("call_transfer_rules", {})),
        "fallback_protocol": "apologize and ask for voicemail"
    }
    
    return spec

def main():
    parser = argparse.ArgumentParser(description="Generate Retell Agent Draft Spec from Memo.")
    parser.add_argument("--memo", required=True, help="Path to input memo JSON file")
    parser.add_argument("--output", required=True, help="Path to save agent spec JSON")
    parser.add_argument("--version", required=True, help="Version (e.g., v1, v2)")
    
    args = parser.parse_args()
    
    with open(args.memo, "r") as f:
        memo = json.load(f)
        
    agent_spec = generate_agent_spec(memo, args.version)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    with open(args.output, "w") as f:
        json.dump(agent_spec, f, indent=4)
        
    logging.info(f"Agent spec {args.version} generated and saved to {args.output}")

if __name__ == "__main__":
    main()
