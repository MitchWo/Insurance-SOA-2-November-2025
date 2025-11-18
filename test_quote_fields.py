#!/usr/bin/env python3
"""
Test the insurance quote fields in assets_liabilities_extractor
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from processors.assets_liabilities_extractor import extract_assets_liabilities

# Test data with insurance quote URLs
test_data = {
    # Basic assets for context
    "16": "500000",  # Owner Occupied Value
    "15": "300000",  # Mortgage

    # Insurance quote upload fields
    "42": "https://example.com/quotes/partners_life_quote.pdf",  # Partners Life
    "43": "https://example.com/quotes/fidelity_life_quote.pdf",  # Fidelity Life
    "44": "",  # AIA - empty
    "45": "https://example.com/quotes/asteron_quote.pdf",  # Asteron
    "46": "",  # Chubb - empty
    "47": "https://example.com/quotes/nib_quote.pdf",  # nib
}

print("=" * 80)
print("TESTING INSURANCE QUOTE FIELDS")
print("=" * 80)

result = extract_assets_liabilities(test_data)

# Check individual quote fields
print("\nIndividual Quote Fields (for Zapier):")
print(f"  quote_partners_life: {result.get('quote_partners_life', 'NOT FOUND')}")
print(f"  quote_fidelity_life: {result.get('quote_fidelity_life', 'NOT FOUND')}")
print(f"  quote_aia: {result.get('quote_aia', 'NOT FOUND') or '(empty)'}")
print(f"  quote_asteron: {result.get('quote_asteron', 'NOT FOUND')}")
print(f"  quote_chubb: {result.get('quote_chubb', 'NOT FOUND') or '(empty)'}")
print(f"  quote_nib: {result.get('quote_nib', 'NOT FOUND')}")

# Check JSON format
print("\nInsurance Quotes JSON:")
quotes_json = json.loads(result.get('insurance_quotes_json', '{}'))
print(json.dumps(quotes_json, indent=2))

# Check text summary
print("\nInsurance Quotes Text Summary:")
if result.get('insurance_quotes_text'):
    print(result['insurance_quotes_text'])
else:
    print("(No quotes text generated)")

# Verify assets/liabilities still work
print("\n" + "=" * 80)
print("VERIFYING ASSETS/LIABILITIES STILL WORK")
print("=" * 80)
print(f"Total Assets: ${result['total_assets']:,}")
print(f"Total Liabilities: ${result['total_liabilities']:,}")
print(f"Net Worth: ${result['net_worth']:,}")

print("\n✅ Test completed successfully!")