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
    # Get email from command line or use default
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = "moresby_isaacs@hotmail.com"

    print("=" * 70)
    print("MANUAL FORM MATCHING AND ZAPIER TRIGGER")
    print("=" * 70)
    print(f"Email: {email}")
    print()

    # Initialize matcher with data directory
    print("Initializing form matcher...")
    matcher = FormMatcher("data/forms")

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
