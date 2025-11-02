#!/usr/bin/env python3
"""
Test script for Complete Field Mappings
Tests the updated FieldMapper and FactFind with all form fields
"""
import sys
import os
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from models.fact_find import FactFind
from field_mapper import FieldMapper


def test_complete_mappings():
    """Test the complete field mappings with comprehensive data"""
    print("=" * 80)
    print("COMPLETE FIELD MAPPINGS TEST")
    print("=" * 80)
    print()

    # Initialize field mapper
    mapper = FieldMapper("config/field_mappings.yaml")

    # Display statistics
    print("MAPPING STATISTICS:")
    print("-" * 60)
    stats = mapper.get_statistics()
    print(f"  Total categories: {stats['total_categories']}")
    print(f"  Total fields: {stats['total_fields']}")
    print()

    print("CATEGORIES BREAKDOWN:")
    print("-" * 60)
    for category, info in stats['categories'].items():
        print(f"  {category:25} : {info['field_count']} fields")
    print()

    # Create comprehensive test data
    test_data = {
        # Admin
        "f516": "CASE-2024-COMPLETE",
        "f219": "john.smith@email.com",
        "f523": "jane.smith@email.com",
        "f8": "couple",

        # Client Profile
        "f144": "John",
        "f145": "Smith",
        "f94": "1980-05-15",
        "f220": "No",
        "f501": "Yes",

        # Partner Profile
        "f146": "Jane",
        "f147": "Smith",
        "f95": "1982-07-20",
        "f252": "No",

        # Employment - Main
        "f482": "No",
        "f6": "Software Engineer",
        "f275": "40",
        "f276": "Full-time",
        "f277": "Tech Corp Ltd",
        "f10": "150000",
        "f279": "25000",
        "f280": "5000",
        "f502": "4",

        # Employment - Partner
        "f483": "Yes",
        "f40": "Business Consultant",
        "f295": "35",
        "f296": "Contract",
        "f297": "Self-employed",
        "f42": "95000",
        "f299": "15000",
        "f300": "0",
        "f503": "0",
        "f304": "3 years",
        "f305": "2",
        "f306": "Yes",
        "f307": "3 months",

        # Property
        "f14": "Own",
        "f84": "123 Main Street, Auckland",
        "f16": "1200000",
        "f15": "650000",
        "f17": "3500",
        "f473": "2500",

        # Children
        "f254": "Yes",
        "f488": "Emma",
        "f490": "2018-03-10",
        "f491": "6",
        "f494": "Oliver",
        "f493": "2020-06-15",
        "f492": "4",

        # Assets
        "f33": "Savings Account",
        "f26": "45000",
        "f19": "Term Deposit",
        "f36": "25000",
        "f35": "Share Portfolio",
        "f34": "85000",

        # Liabilities
        "f71": "Credit Card",
        "f72": "5000",
        "f73": "Car Loan",
        "f74": "15000",

        # Investment Properties
        "f140": "Yes",
        "f119": "45 Rental Street, Wellington",
        "f21": "650000",
        "f27": "400000",
        "f28": "650",
        "f485": "No",

        # KiwiSaver
        "f60": "ANZ",
        "f61": "Growth",
        "f62": "75000",
        "f63": "Westpac",
        "f64": "Balanced",
        "f65": "62000",

        # Medical - Main
        "f223": "None",
        "f225": "No",
        "f331": "None",
        "f332": "None",
        "f512": "180cm",
        "f513": "82kg",
        "f335": "25.3",
        "f524": "Dr Smith, Auckland Medical Centre",

        # Medical - Partner
        "f224": "Asthma - mild",
        "f226": "Yes",
        "f337": "Mild asthma",
        "f338": "Ventolin as needed",
        "f514": "165cm",
        "f515": "62kg",
        "f341": "22.8",

        # Existing Insurance - Main
        "f344": "500000",
        "f345": "AIA",
        "f348": "250000",
        "f349": "Partners Life",
        "f350": "6000",
        "f351": "Southern Cross",
        "f352": "4 weeks / 2 years",
        "f356": "450",

        # Existing Insurance - Partner
        "f358": "400000",
        "f359": "AIA",
        "f362": "200000",
        "f363": "Partners Life",
        "f364": "4500",
        "f365": "Southern Cross",
        "f370": "380",

        # Recreational
        "f374": "No",
        "f377": "Protect family, ensure mortgage covered, income protection",

        # Needs Analysis - Life
        "f380": "650000",
        "f381": "300000",
        "f382": "200000",
        "f383": "25000",
        "f391": "650000",
        "f392": "400000",

        # Needs Analysis - Trauma
        "f402": "150000",
        "f486": "50000",
        "f404": "50000",
        "f411": "120000",
        "f487": "40000",

        # Needs Analysis - Income Protection
        "f420": "3500",
        "f421": "2500",
        "f423": "Indemnity",
        "f430": "8",
        "f431": "2",
        "f433": "3500",
        "f434": "2500",

        # Scope of Advice
        "f520.1": "Yes",
        "f520.2": "Yes",
        "f520.3": "Yes",
        "f520.4": "Yes",
        "f522": "Full comprehensive review requested"
    }

    # Create fact find with mapper
    print("LOADING FACT FIND WITH COMPLETE MAPPINGS:")
    print("-" * 60)
    fact_find = FactFind(use_field_mapper=True)
    fact_find.load_from_dict(test_data)

    # Display loaded sections
    sections_to_check = [
        ('case_info', 'Case Information'),
        ('client_info', 'Client Information'),
        ('partner_info', 'Partner Information'),
        ('employment_main', 'Employment - Main'),
        ('employment_partner', 'Employment - Partner'),
        ('household_info', 'Household'),
        ('assets', 'Assets'),
        ('liabilities', 'Liabilities'),
        ('investment_properties', 'Investment Properties'),
        ('kiwisaver', 'KiwiSaver'),
        ('medical_main', 'Medical - Main'),
        ('medical_partner', 'Medical - Partner'),
        ('existing_insurance_main', 'Insurance - Main'),
        ('existing_insurance_partner', 'Insurance - Partner'),
        ('recreational', 'Recreational'),
        ('needs_life_main', 'Needs Analysis - Life (Main)'),
        ('needs_trauma_main', 'Needs Analysis - Trauma (Main)'),
        ('needs_income_main', 'Needs Analysis - Income (Main)'),
        ('scope_of_advice', 'Scope of Advice')
    ]

    populated_sections = 0
    for attr_name, display_name in sections_to_check:
        section_data = getattr(fact_find, attr_name, {})
        if section_data and any(section_data.values()):
            populated_sections += 1
            print(f"✓ {display_name:30} : {len(section_data)} fields populated")

    print()
    print(f"Total sections populated: {populated_sections}/{len(sections_to_check)}")
    print()

    # Detailed verification
    print("DETAILED VERIFICATION:")
    print("-" * 60)

    checks = [
        ("Case ID", fact_find.case_info.get('case_id'), "CASE-2024-COMPLETE"),
        ("Client name", fact_find.get_client_full_name(), "John Smith"),
        ("Partner name", fact_find.get_partner_full_name(), "Jane Smith"),
        ("Client occupation", fact_find.employment_main.get('occupation'), "Software Engineer"),
        ("Partner self-employed", fact_find.employment_partner.get('self_employed'), "Yes"),
        ("House value", fact_find.household_info.get('current_house_value'), 1200000.0),
        ("Child 1 name", fact_find.children.get('child_1_name'), "Emma"),
        ("KiwiSaver main balance", fact_find.kiwisaver.get('main_balance'), 75000.0),
        ("Investment property value", fact_find.investment_properties.get('property_1_value'), 650000.0),
        ("Life cover main", fact_find.existing_insurance_main.get('life_cover_amount'), 500000.0),
        ("Medical main BMI", fact_find.medical_main.get('bmi'), "25.3"),
        ("Recreational activities", fact_find.recreational.get('high_risk_activities'), "No"),
        ("Needs life debt", fact_find.needs_life_main.get('debt_repayment'), 650000.0),
        ("Scope - Life Insurance", fact_find.scope_of_advice.get('life_insurance'), "Yes")
    ]

    passed = 0
    failed = 0
    for check_name, actual, expected in checks:
        if actual == expected:
            print(f"  ✓ {check_name:25} : {actual}")
            passed += 1
        else:
            print(f"  ✗ {check_name:25} : got {actual}, expected {expected}")
            failed += 1

    print()
    print("=" * 80)
    if failed == 0:
        print(f"SUCCESS: All {passed} verification checks passed!")
        print("The complete field mapping system is working correctly.")
    else:
        print(f"PARTIAL SUCCESS: {passed} passed, {failed} failed")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = test_complete_mappings()
    sys.exit(0 if success else 1)