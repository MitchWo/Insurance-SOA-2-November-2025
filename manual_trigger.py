#!/usr/bin/env python3
"""
Manual trigger script to match forms and trigger Zapier
"""

import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.fact_find import FactFind
from models.automation_form import AutomationForm
from processors.form_matcher import FormMatcher
from processors.auto_matcher import check_and_trigger_match
from processors.zapier_trigger import ZapierTrigger

def main():
    email = "ryandmi@gmail.com"

    print("=" * 70)
    print("MANUAL FORM MATCHING AND ZAPIER TRIGGER")
    print("=" * 70)
    print(f"Email: {email}")
    print()

    # Load forms
    fact_find_path = Path("data/forms/fact_finds/ryandmi_at_gmail_com_20251105_044959.json")
    automation_path = Path("data/forms/automation_forms/ryandmi_at_gmail_com_20251105_045213.json")

    print(f"Loading fact find from: {fact_find_path}")
    with open(fact_find_path, 'r') as f:
        fact_find_data = json.load(f)

    print(f"Loading automation form from: {automation_path}")
    with open(automation_path, 'r') as f:
        automation_data = json.load(f)

    # Create models
    print("\nCreating form models...")
    fact_find = FactFind()
    fact_find.load_from_dict(fact_find_data)

    automation_form = AutomationForm()
    automation_form.load_from_dict(automation_data)

    # Create matcher and add forms
    print("Creating matcher...")
    matcher = FormMatcher()
    matcher.add_fact_find(fact_find)
    matcher.add_automation_form(automation_form)

    # Create Zapier trigger
    print("Creating Zapier trigger...")
    zapier_trigger = ZapierTrigger()

    # Trigger matching and Zapier
    print("\nTriggering match and Zapier...")
    print("=" * 70)
    result = check_and_trigger_match(email, matcher, zapier_trigger)

    print("\n" + "=" * 70)
    print("RESULT")
    print("=" * 70)
    print(json.dumps(result, indent=2, default=str))

    if result.get('zapier_triggered'):
        print("\n✅ SUCCESS: Zapier webhook triggered successfully!")
        if result.get('report_path'):
            print(f"📄 Reports generated at: {result.get('report_path')}")
    else:
        print("\n❌ FAILED: Zapier webhook was not triggered")
        print(f"Reason: {result.get('message')}")

if __name__ == "__main__":
    main()
