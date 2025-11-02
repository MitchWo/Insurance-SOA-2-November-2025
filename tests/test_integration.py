#!/usr/bin/env python3
"""
Integration Test for Fact Find with Field Mapper
Tests the complete flow of loading and mapping fact find data
"""
import sys
import os
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from models.fact_find import FactFind
from field_mapper import FieldMapper


def test_fact_find_integration():
    """Test the complete fact find integration with field mapper"""
    print("=" * 70)
    print("FACT FIND INTEGRATION TEST")
    print("=" * 70)
    print()

    # Test data with comprehensive fields
    test_data = {
        "f516": "CASE-2024-001",
        "f144": "John",
        "f145": "Smith",
        "f219": "john.smith@email.com",
        "f94": "1980-05-15",
        "f6": "Software Engineer",
        "f10": "120000",
        "f15": "450000",
        "f16": "850000",
        "f220": "No",
        "f8": "couple",
        "f14": "Own",
        "f254": "Yes",
        "f255": "2",
        # Partner data
        "f146": "Jane",
        "f147": "Doe",
        "f95": "1982-07-20",
        "f40": "Teacher",
        "f42": "75000",
        "f252": "No",
        # Additional assets
        "f62": "45000",  # KiwiSaver client
        "f65": "38000",  # KiwiSaver partner
        "f26": "25000",  # Savings
        # Existing insurance
        "f344": "500000",  # Life cover
        "f345": "AIA",     # Life provider
        "f348": "250000",  # Trauma cover
        "f349": "Partners Life"  # Trauma provider
    }

    # Create fact find with field mapper
    print("TESTING WITH FIELD MAPPER:")
    print("-" * 50)
    fact_find_mapped = FactFind(use_field_mapper=True)
    fact_find_mapped.load_from_dict(test_data)

    print("Client Information:")
    for key, value in fact_find_mapped.client_info.items():
        print(f"  {key}: {value}")
    print()

    print("Partner Information:")
    if fact_find_mapped.partner_info:
        for key, value in fact_find_mapped.partner_info.items():
            print(f"  {key}: {value}")
    else:
        print("  No partner information")
    print()

    print("Household Information:")
    for key, value in fact_find_mapped.household_info.items():
        print(f"  {key}: {value}")
    print()

    print("Assets:")
    for key, value in fact_find_mapped.assets.items():
        if isinstance(value, float):
            print(f"  {key}: ${value:,.2f}")
        else:
            print(f"  {key}: {value}")
    print()

    print("Existing Insurance:")
    for key, value in fact_find_mapped.existing_insurance.items():
        if isinstance(value, float):
            print(f"  {key}: ${value:,.2f}")
        else:
            print(f"  {key}: {value}")
    print()

    print("Case Info:")
    for key, value in fact_find_mapped.case_info.items():
        print(f"  {key}: {value}")
    print()

    # Test backward compatibility
    print("BACKWARD COMPATIBILITY TEST:")
    print("-" * 50)
    fact_find_legacy = FactFind(use_field_mapper=False)
    fact_find_legacy.load_from_dict(test_data)

    print("Legacy extraction (without field mapper):")
    print(f"  Client name: {fact_find_legacy.get_client_full_name()}")
    print(f"  Case ID: {fact_find_legacy.case_info.get('case_id')}")
    print(f"  Mortgage: ${fact_find_legacy.financial_info.get('mortgage'):,.2f}" if fact_find_legacy.financial_info.get('mortgage') else "  Mortgage: None")
    print()

    # Verify critical fields
    print("VERIFICATION:")
    print("-" * 50)
    checks = [
        ("Field mapper initialized", fact_find_mapped.field_mapper is not None),
        ("Case ID extracted", fact_find_mapped.case_info.get('case_id') == "CASE-2024-001"),
        ("Client name extracted", fact_find_mapped.get_client_full_name() == "John Smith"),
        ("Partner detected", fact_find_mapped.is_couple()),
        ("Partner name extracted", fact_find_mapped.get_partner_full_name() == "Jane Doe"),
        ("Client income parsed", fact_find_mapped.employment_main.get('annual_income') == 120000.0),
        ("Partner income parsed", fact_find_mapped.employment_partner.get('annual_income') == 75000.0),
        ("Assets extracted", len(fact_find_mapped.assets) > 0),
        ("Insurance extracted", len(fact_find_mapped.existing_insurance_main) > 0),
        ("Household extracted", len(fact_find_mapped.household_info) > 0),
    ]

    all_passed = True
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {check_name}")
        if not result:
            all_passed = False

    # Test JSON export
    print()
    print("JSON EXPORT TEST:")
    print("-" * 50)
    exported = fact_find_mapped.to_dict()
    print(f"  Exported keys: {list(exported.keys())}")
    print(f"  Has all sections: {len(exported) >= 10}")

    print()
    print("=" * 70)
    if all_passed:
        print("SUCCESS: All integration tests passed!")
        print("The field mapper is working correctly with the FactFind model.")
    else:
        print("FAILURE: Some integration tests failed")
    print("=" * 70)

    return all_passed


if __name__ == "__main__":
    success = test_fact_find_integration()
    sys.exit(0 if success else 1)