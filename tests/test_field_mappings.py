#!/usr/bin/env python3
"""
Test script for Field Mappings
Tests the FieldMapper functionality with sample data
"""
import sys
import os
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from field_mapper import FieldMapper


def test_field_mapper():
    """Test the field mapper with sample data"""
    print("=" * 70)
    print("FIELD MAPPER TEST")
    print("=" * 70)
    print()

    # Initialize the field mapper
    try:
        mapper = FieldMapper()
        print("✓ Field mapper initialized successfully")
        print(f"  Configuration loaded from: {mapper.config_path}")
        print()
    except FileNotFoundError as e:
        print(f"✗ Failed to initialize field mapper: {e}")
        return False

    # Display mapping statistics
    print("MAPPING STATISTICS:")
    print("-" * 50)
    stats = mapper.get_statistics()
    print(f"  Total categories: {stats['total_categories']}")
    print(f"  Total fields: {stats['total_fields']}")
    print()

    print("CATEGORIES AND FIELD COUNTS:")
    print("-" * 50)
    for category in mapper.get_all_categories():
        field_count = mapper.get_field_count(category)
        print(f"  {category:20} : {field_count} fields")
    print()

    # Test data with both "f" prefix and without
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
        "f8": "single",
        "f14": "Own",
        "f254": "Yes",
        "f255": "2",
        "146": "Jane",  # Test without "f" prefix
        "147": "Doe",
        "95": "1982-07-20",
        "40": "Teacher",
        "42": "75000"
    }

    print("TEST DATA EXTRACTION:")
    print("-" * 50)
    print("Sample data contains both 'f' prefixed and plain field IDs")
    print()

    # Test specific field extraction
    print("INDIVIDUAL FIELD TESTS:")
    print("-" * 50)

    test_cases = [
        ("client", "first_name", "John"),
        ("client", "last_name", "Smith"),
        ("client", "email", "john.smith@email.com"),
        ("client", "annual_income", "120000"),
        ("partner", "first_name", "Jane"),
        ("partner", "last_name", "Doe"),
        ("household", "relationship_status", "single"),
        ("assets", "home_value", "850000"),
        ("admin", "case_id", "CASE-2024-001")
    ]

    passed = 0
    failed = 0

    for category, field_name, expected in test_cases:
        value = mapper.get_field(test_data, category, field_name)
        if value == expected:
            print(f"  ✓ {category}.{field_name}: '{value}'")
            passed += 1
        else:
            print(f"  ✗ {category}.{field_name}: got '{value}', expected '{expected}'")
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed")
    print()

    # Test category extraction
    print("CATEGORY EXTRACTION TEST:")
    print("-" * 50)

    client_data = mapper.extract_category(test_data, "client")
    print("Client data extracted:")
    for field, value in client_data.items():
        print(f"  {field}: {value}")
    print()

    partner_data = mapper.extract_category(test_data, "partner")
    print("Partner data extracted:")
    for field, value in partner_data.items():
        print(f"  {field}: {value}")
    print()

    # Test full extraction
    print("FULL DATA EXTRACTION:")
    print("-" * 50)
    all_data = mapper.extract_all(test_data)
    print(f"Categories with data: {list(all_data.keys())}")
    print()

    # Test field description
    print("FIELD DESCRIPTION TEST:")
    print("-" * 50)
    test_field_ids = ["144", "516", "220", "999"]

    for field_id in test_field_ids:
        desc = mapper.describe_field(field_id)
        if desc:
            print(f"  Field {field_id}: {desc['category']}.{desc['field_name']}")
        else:
            print(f"  Field {field_id}: Not mapped")
    print()

    # Load and test with actual sample data
    print("INTEGRATION TEST WITH SAMPLE DATA:")
    print("-" * 50)
    sample_path = Path("data/sample_fact_find.json")

    if sample_path.exists():
        with open(sample_path, 'r') as f:
            sample_data = json.load(f)

        extracted = mapper.extract_all(sample_data)

        print("Extracted categories from sample_fact_find.json:")
        for category, fields in extracted.items():
            print(f"  {category}: {len(fields)} fields")
            for field_name, value in list(fields.items())[:3]:  # Show first 3
                display_value = str(value)[:30] + "..." if len(str(value)) > 30 else str(value)
                print(f"    - {field_name}: {display_value}")
        print()
    else:
        print("  Sample data file not found")
        print()

    # Final summary
    print("=" * 70)
    if failed == 0:
        print("SUCCESS: All field mapping tests passed!")
    else:
        print(f"PARTIAL SUCCESS: {passed} tests passed, {failed} tests failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = test_field_mapper()
    sys.exit(0 if success else 1)