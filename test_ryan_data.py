#!/usr/bin/env python3
"""
Test the assets and liabilities extractor with Ryan's actual data
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from processors.assets_liabilities_extractor import extract_assets_liabilities

# Ryan's actual data from the fact find
ryan_data = {
    "6": "IT Infrastructure Engineer",
    "8": "My partner and I",
    "10": "110000",
    "14": "Own",
    "15": "522000",  # Current Mortgage Value
    "16": "725000",  # Owner Occupied Value
    "17": "4200",
    "19": "Managed Funds - Foodstuffs Provident Fund",  # Asset 2 name per spec
    "22": "",  # Asset 1 name per spec (EMPTY in Ryan's data!)
    "26": "16000",  # Asset 1 value per spec (but no name!)
    "33": "Managed Funds - Investnow",  # NOT IN SPEC but has data!
    "34": "",  # Asset 3 value per spec
    "35": "",  # Asset 3 name per spec
    "36": "80000",  # Asset 2 value per spec
    "45": "",  # Asset 4 name
    "46": "",  # Asset 4 value
    "47": "",  # Asset 5 name
    "60": "Booster",  # Main KiwiSaver Provider
    "62": "55253",  # Main KiwiSaver Balance
    "63": "Booster",  # Partner KiwiSaver Provider
    "65": "31113",  # Partner KiwiSaver Balance
    "71": "Credit Card",  # Liability 1 name
    "72": "3100",  # Liability 1 value
    "73": "",  # Liability 2 name
    "74": "",  # Liability 2 value
    "287": "",  # Asset 5 value per spec
    "466": "96000",  # Asset Total
    "468": "0",  # Total Investment Property Value
    "469": "0",  # Total Investment Property Debt
}

print("=" * 80)
print("RYAN'S DATA ANALYSIS")
print("=" * 80)
print("\nAssets found in data:")
print(f"  Primary Residence: ${725000:,} (field 16)")
print(f"  Mortgage: ${522000:,} (field 15)")
print(f"  Asset at field 19/36: {ryan_data['19']} = ${80000:,}")
print(f"  Asset at field 33/?: 'Managed Funds - Investnow' (no value field in spec!)")
print(f"  Orphan value at field 26: ${16000:,} (no name in field 22)")
print(f"  KiwiSaver Main: Booster = ${55253:,}")
print(f"  KiwiSaver Partner: Booster = ${31113:,}")
print(f"  Asset Total (field 466): ${96000:,}")
print("\nLiabilities found:")
print(f"  Mortgage: ${522000:,}")
print(f"  Credit Card: ${3100:,}")

print("\n" + "=" * 80)
print("RUNNING EXTRACTOR WITH CURRENT MAPPINGS")
print("=" * 80)

result = extract_assets_liabilities(ryan_data)

print("\n" + result['assets_text'])
print("\n" + result['liabilities_text'])
print("\n" + result['summary_text'])

if result.get('validation_note'):
    print("\n⚠️  " + result['validation_note'])

# Detailed breakdown
assets = json.loads(result['assets_json'])
print("\n" + "=" * 80)
print("EXTRACTED ASSETS:")
for i, asset in enumerate(assets, 1):
    print(f"  {i}. {asset['name']}: {asset['formatted']}")

print(f"\nCalculated Total: ${result['total_assets']:,}")
print(f"Form Total (466): ${result.get('form_asset_total', 0):,}")

print("\n" + "=" * 80)
print("ISSUES FOUND:")
print("=" * 80)
print("1. Field 33 ('Managed Funds - Investnow') is not in the specification")
print("2. Field 26 has value $16,000 but field 22 (its name field) is empty")
print("3. Field 466 shows $96,000 but this doesn't match expected total")
print("   (Should be ~$962,366 if including house, KiwiSaver, and funds)")