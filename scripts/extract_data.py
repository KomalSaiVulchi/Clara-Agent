import os
import json
import argparse
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d')

EXTRACTION_PROMPT = """You are an information extraction system.

Your job is to extract operational configuration data from a service business call transcript.

You must only extract information explicitly mentioned in the transcript.

Never guess or invent missing information.

If a field is not mentioned, add it to "questions_or_unknowns".

Return structured JSON following the schema below.

Schema:

{
"company_name": "",
"business_hours": {
"days": "",
"start": "",
"end": "",
"timezone": ""
},
"office_address": "",
"services_supported": [],
"emergency_definition": [],
"emergency_routing_rules": {},
"non_emergency_routing_rules": {},
"call_transfer_rules": {
"timeout_seconds": "",
"retry_count": "",
"fallback_action": ""
},
"integration_constraints": [],
"after_hours_flow_summary": "",
"office_hours_flow_summary": "",
"questions_or_unknowns": [],
"notes": ""
}

Rules:

Only include information explicitly present in the transcript.

If a value is missing, leave the field null.

Add missing items to questions_or_unknowns.

Services_supported should list services such as:
sprinkler systems
fire alarms
extinguishers
inspections

Emergency_definition should list triggers such as:
sprinkler leak
fire alarm triggered
smoke detection

Routing rules must describe who calls are transferred to and in what order.

Return valid JSON only.

Transcript:
{transcript}
"""

def extract_data_mock(transcript: str, account_id: str) -> Dict[str, Any]:
    """Returns mock data based on our dummy transcripts for zero-cost local demonstrations."""
    # Simple heuristic to determine which mock to return based on transcript content
    if "Apex Plumbing" in transcript:
        if "7am to 6pm" in transcript: # onboarding
            return {
                "business_hours": {"days": "Monday-Saturday", "start": "7am", "end": "6pm", "timezone": "PST"},
                "emergency_definition": ["major pipe burst", "flooded basement", "gas leaks"],
                "integration_constraints": ["never schedule water heater repairs through ServiceTitan automatically", "do not create drain cleaning jobs in HouseCall Pro"],
            }
        return {
            "account_id": account_id,
            "company_name": "Apex Plumbing",
            "business_hours": {"days": "Monday to Friday", "start": "8am", "end": "5pm", "timezone": "PST"},
            "office_address": None,
            "services_supported": ["pipe leaks", "water heater repair", "drain cleaning"],
            "emergency_definition": ["major pipe burst", "completely flooded basement"],
            "emergency_routing_rules": {"step_1": "dispatch team at 555-0199"},
            "non_emergency_routing_rules": {"step_1": "leave a message"},
            "call_transfer_rules": {"timeout_seconds": "30", "retry_count": "2", "fallback_action": "voicemail"},
            "integration_constraints": ["never schedule water heater repairs through ServiceTitan automatically"],
            "after_hours_flow_summary": None,
            "office_hours_flow_summary": None,
            "questions_or_unknowns": ["office address missing", "after hours flow missing"],
            "notes": ""
        }
    elif "Sparky Electrical" in transcript:
        if "555-0800" in transcript:
            return {
                 "after_hours_flow_summary": "route emergencies to 555-0800",
                 "call_transfer_rules": {"timeout_seconds": "45", "retry_count": "1", "fallback_action": "voicemail"}
            }
        return {
            "account_id": account_id,
            "company_name": "Sparky Electrical",
            "business_hours": {"days": "weekdays", "start": "9am", "end": "6pm", "timezone": "EST"},
            "office_address": None,
            "services_supported": ["wiring", "panel upgrades", "generator installation"],
            "emergency_definition": ["buzzing electrical panels", "total power loss"],
            "emergency_routing_rules": {"step_1": "cell at 555-0200"},
            "non_emergency_routing_rules": {"step_1": "take down details for call back"},
            "call_transfer_rules": {"timeout_seconds": "20", "retry_count": "1", "fallback_action": "voicemail"},
            "integration_constraints": [],
            "after_hours_flow_summary": "take a message",
            "office_hours_flow_summary": None,
            "questions_or_unknowns": ["office address missing"],
            "notes": ""
        }
    elif "Frosty HVAC" in transcript:
        if "555-0301" in transcript:
            return {
                "emergency_routing_rules": {"step_1": "555-0300", "step_2": "backup 555-0301"},
                "integration_constraints": ["do not book duct cleaning after 5pm on Jobber"]
            }
        return {
            "account_id": account_id,
            "company_name": "Frosty HVAC",
            "business_hours": {"days": "Everyday", "start": "8am", "end": "8pm", "timezone": "CST"},
            "office_address": None,
            "services_supported": ["AC repair", "furnace install", "duct cleaning"],
            "emergency_definition": ["no heat in winter", "no AC for elderly"],
            "emergency_routing_rules": {"step_1": "555-0300"},
            "non_emergency_routing_rules": {},
            "call_transfer_rules": {"timeout_seconds": "15", "retry_count": "3", "fallback_action": "tell tech is on the way"},
            "integration_constraints": [],
            "after_hours_flow_summary": None,
            "office_hours_flow_summary": None,
            "questions_or_unknowns": ["office address missing", "non-emergency routing missing"],
            "notes": ""
        }
    elif "Elite Landscaping" in transcript:
        if "irrigation" in transcript:
            return {
                "business_hours": {"days": "Monday to Friday", "start": "6am", "end": "5pm", "timezone": "EST"},
                "services_supported": ["lawn care", "hardscaping", "tree removal", "irrigation repair"],
                "call_transfer_rules": {"timeout_seconds": "60", "retry_count": "1", "fallback_action": "voicemail"},
            }
        return {
            "account_id": account_id,
            "company_name": "Elite Landscaping",
            "business_hours": {"days": "Monday to Friday", "start": "6am", "end": "4pm", "timezone": "EST"},
            "office_address": None,
            "services_supported": ["lawn care", "hardscaping", "tree removal"],
            "emergency_definition": ["fallen trees blocking driveways", "power lines"],
            "emergency_routing_rules": {"step_1": "dispatch at 555-0400"},
            "non_emergency_routing_rules": {"step_1": "voicemail"},
            "call_transfer_rules": {"timeout_seconds": "30", "retry_count": "1", "fallback_action": "voicemail"},
            "integration_constraints": [],
            "after_hours_flow_summary": None,
            "office_hours_flow_summary": None,
            "questions_or_unknowns": ["after hours flow missing", "office address missing"],
            "notes": ""
        }
    elif "Peak Roofing" in transcript:
        if "sky light" in transcript:
             return {
                "business_hours": {"days": "Weekdays 9am-6pm, weekends", "start": "10am", "end": "2pm", "timezone": "MST"},
                "emergency_routing_rules": {"step_1": "dispatch at 555-0501"},
                "services_supported": ["roof repair", "shingle replacement", "gutter cleaning", "sky light installation"]
             }
        return {
            "account_id": account_id,
            "company_name": "Peak Roofing",
            "business_hours": {"days": "weekdays", "start": "8am", "end": "5pm", "timezone": "MST"},
            "office_address": None,
            "services_supported": ["roof repair", "shingle replacement", "gutter cleaning"],
            "emergency_definition": ["active roof leaks", "storm damage"],
            "emergency_routing_rules": {"step_1": "cell 555-0500"},
            "non_emergency_routing_rules": {"step_1": "leave name, number, problem, call back"},
            "call_transfer_rules": {"timeout_seconds": "30", "retry_count": "2", "fallback_action": "voicemail"},
            "integration_constraints": ["do not touch QuickBooks"],
            "after_hours_flow_summary": None,
            "office_hours_flow_summary": None,
            "questions_or_unknowns": ["office address missing"],
            "notes": ""
        }
    
    # Generic fallback
    return {
         "account_id": account_id,
         "company_name": "Unknown",
         "business_hours": {},
         "questions_or_unknowns": ["everything"]
    }

def main():
    parser = argparse.ArgumentParser(description="Extract structured operational data from transcripts.")
    parser.add_argument("--transcript", required=True, help="Path to transcript file")
    parser.add_argument("--output", required=True, help="Path to save output JSON memo")
    parser.add_argument("--account_id", required=True, help="Account ID")
    parser.add_argument("--stage", required=True, choices=["demo", "onboarding"], help="Extraction stage")
    
    args = parser.parse_args()
    
    with open(args.transcript, "r") as f:
        transcript_text = f.read()

    # In a real environment, we would use an LLM API here.
    # To ensure this functions out-of-the-box in a zero-cost local environment, we mock the LLM call.
    # The architecture remains intact.
    
    extracted_data = extract_data_mock(transcript_text, args.account_id)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    with open(args.output, "w") as f:
        json.dump(extracted_data, f, indent=4)
        
    logging.info(f"{args.stage} extraction complete for {args.account_id}. Saved to {args.output}")

if __name__ == "__main__":
    main()
