#!/usr/bin/env python3
"""
Test script to verify insurance quotes are being extracted and sent to Zapier
"""

import sys
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from processors.auto_matcher import check_and_trigger_match
from processors.zapier_trigger import ZapierTrigger

def main():
    # Get email from command line or use default
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = "moresby_isaacs@hotmail.com"

    print("=" * 70)
    print("INSURANCE QUOTES TEST")
    print("=" * 70)
    print(f"Testing email: {email}")
    print()

    # Create a mock FormMatcher that loads from disk
    class MockFormMatcher:
        def match_by_email(self, email_addr):
            # Load forms directly from disk
            safe_email = email_addr.replace('@', '_at_').replace('.', '_')

            # Load fact find
            fact_find_data = None
            fact_find_dir = Path("data/forms/fact_finds")
            for ff in fact_find_dir.glob(f"{safe_email}*.json"):
                with open(ff) as f:
                    fact_find_data = json.load(f)
                    break

            # Load automation form
            automation_data = None
            automation_dir = Path("data/forms/automation_forms")
            for af in automation_dir.glob(f"{safe_email}*.json"):
                with open(af) as f:
                    automation_data = json.load(f)
                    break

            if not fact_find_data or not automation_data:
                return None

            # Create mock result
            class MockResult:
                def __init__(self, ff, af):
                    self.fact_find = type('FF', (), {'to_dict': lambda: ff, 'raw_data': ff})()
                    self.automation_form = type('AF', (), {'to_dict': lambda: af, 'raw_data': af})()
                    self.confidence = 1.0

                def is_confident_match(self, threshold=0.6):
                    return True

            return MockResult(fact_find_data, automation_data)

    # Create instances
    matcher = MockFormMatcher()
    zapier_trigger = ZapierTrigger()

    # Trigger matching and Zapier
    print("Checking for forms and triggering Zapier...")
    print("=" * 70)
    result = check_and_trigger_match(email, matcher, zapier_trigger)

    # Extract insurance quotes section
    if result.get('combined_data'):
        quotes = result['combined_data'].get('insurance_quotes', {})
        print("\nINSURANCE QUOTES SECTION:")
        print("-" * 40)
        if quotes:
            print(f"Section ID: {quotes.get('section_id')}")
            print(f"Has quotes: {quotes.get('has_quotes')}")
            print(f"Quotes count: {quotes.get('quotes_count')}")
            print()
            print("Individual quotes:")
            for provider in ['partners_life', 'fidelity_life', 'aia', 'asteron', 'chubb', 'nib']:
                quote_key = f"quote_{provider}"
                quote_url = quotes.get(quote_key, '')
                if quote_url:
                    print(f"  {provider}: {quote_url[:80]}...")
                else:
                    print(f"  {provider}: [No quote uploaded]")
        else:
            print("ERROR: No insurance_quotes section found in combined data!")

    print("\n" + "=" * 70)
    print("FULL RESULT:")
    print("=" * 70)
    print(json.dumps(result, indent=2, default=str))

    if result.get('zapier_triggered'):
        print("\n✅ SUCCESS: Zapier webhook triggered successfully!")
        print("Check Zapier to verify the insurance_quotes section is present")
    else:
        print("\n❌ FAILED: Zapier webhook was not triggered")
        print(f"Reason: {result.get('message')}")

if __name__ == "__main__":
    main()