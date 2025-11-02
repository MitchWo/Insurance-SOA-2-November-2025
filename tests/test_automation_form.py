#!/usr/bin/env python3
"""
Test script for Automation Form
Tests the AutomationForm model and field mappings
"""
import sys
import os
import json
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from models.automation_form import AutomationForm
from field_mapper import FieldMapper


def test_automation_form():
    """Test the automation form with sample data"""
    print("=" * 70)
    print("AUTOMATION FORM TEST")
    print("=" * 70)
    print()

    # Initialize field mapper for automation form
    mapper = FieldMapper("config/automation_form_mappings.yaml")

    # Display statistics
    print("MAPPING STATISTICS:")
    print("-" * 50)
    stats = mapper.get_statistics()
    print(f"  Total categories: {stats['total_categories']}")
    print(f"  Total fields: {stats['total_fields']}")
    print()

    print("CATEGORIES:")
    print("-" * 50)
    for category in mapper.get_all_categories():
        field_count = mapper.get_field_count(category)
        print(f"  {category:25} : {field_count} fields")
    print()

    # Create test data for automation form
    test_data = {
        # Client details
        "f3": "john.smith@email.com",
        "f39": "couple",

        # Scope of advice
        "f5": "Yes",  # Main checkbox
        "f5.1": "Yes",  # Life Insurance
        "f5.2": "Yes",  # Income Protection
        "f5.3": "Yes",  # Trauma Cover
        "f5.4": "No",   # Health Insurance
        "f5.5": "Yes",  # TPD
        "f5.6": "No",   # ACC

        # Limitations
        "f6": "Yes",
        "f6.1": "No",   # Employer medical
        "f6.2": "No",   # No debt
        "f6.3": "Yes",  # Budget limitations
        "f6.4": "No",   # Self insure
        "f6.5": "No",   # No dependants
        "f6.6": "No",   # Uninsurable occupation
        "f6.7": "No",   # Other
        "f7": "Client has budget constraints, limiting to essential covers only",

        # Main existing cover
        "f11": "500000",  # Life amount
        "f12": "AIA",     # Life provider
        "f13": "0",       # TPD amount
        "f14": "",        # TPD provider
        "f15": "250000",  # Trauma amount
        "f16": "Partners Life",  # Trauma provider
        "f17": "5000",    # Income protection amount
        "f18": "Southern Cross",  # Income protection provider
        "f19": "4 weeks / 2 years",  # IP periods
        "f20": "0",       # Medical amount
        "f21": "",        # Medical provider
        "f22": "",        # Medical excess/addons
        "f23": "450",     # Existing premiums

        # Partner existing cover
        "f49": "300000",  # Life amount
        "f50": "AIA",     # Life provider
        "f51": "0",       # TPD amount
        "f52": "",        # TPD provider
        "f53": "200000",  # Trauma amount
        "f54": "Partners Life",  # Trauma provider
        "f55": "4000",    # Income protection amount
        "f56": "Southern Cross",  # Income protection provider
        "f57": "4 weeks / 2 years",  # IP periods
        "f58": "0",       # Medical amount
        "f59": "",        # Medical provider
        "f60": "",        # Medical excess/addons
        "f61": "380",     # Existing premiums

        # Recommendations
        "f41": "Partners Life",  # Selected provider
        "f42": "850",     # Partners Life quote
        "f43": "920",     # Fidelity Life quote
        "f44": "875",     # AIA quote
        "f45": "910",     # Asteron quote
        "f46": "",        # Chubb quote (not provided)
        "f47": "1050"     # nib quote
    }

    # Create automation form and load data
    print("LOADING AUTOMATION FORM:")
    print("-" * 50)
    form = AutomationForm()
    form.load_from_dict(test_data)

    print("Client Details:")
    for key, value in form.client_details.items():
        print(f"  {key}: {value}")
    print()

    print("Scope of Advice:")
    selected_scope = form.get_selected_scope()
    print(f"  Selected insurance types: {', '.join(selected_scope)}")
    print()

    print("Limitations:")
    limitation_reasons = form.get_limitation_reasons()
    if limitation_reasons:
        print(f"  Reasons: {', '.join(limitation_reasons)}")
    if form.limitations.get('limitation_notes'):
        print(f"  Notes: {form.limitations['limitation_notes']}")
    print()

    print("Main Contact Existing Cover:")
    print(f"  Life: ${form.main_existing_cover.get('life_amount', 0):,.0f} ({form.main_existing_cover.get('life_provider', 'N/A')})")
    print(f"  Trauma: ${form.main_existing_cover.get('trauma_amount', 0):,.0f} ({form.main_existing_cover.get('trauma_provider', 'N/A')})")
    print(f"  Income Protection: ${form.main_existing_cover.get('income_protection_amount', 0):,.0f} ({form.main_existing_cover.get('income_protection_provider', 'N/A')})")
    print(f"  Existing Premiums: ${form.main_existing_cover.get('existing_premiums', 0):,.0f}")
    print()

    if form.is_couple():
        print("Partner Existing Cover:")
        print(f"  Life: ${form.partner_existing_cover.get('life_amount', 0):,.0f} ({form.partner_existing_cover.get('life_provider', 'N/A')})")
        print(f"  Trauma: ${form.partner_existing_cover.get('trauma_amount', 0):,.0f} ({form.partner_existing_cover.get('trauma_provider', 'N/A')})")
        print(f"  Income Protection: ${form.partner_existing_cover.get('income_protection_amount', 0):,.0f} ({form.partner_existing_cover.get('income_protection_provider', 'N/A')})")
        print(f"  Existing Premiums: ${form.partner_existing_cover.get('existing_premiums', 0):,.0f}")
        print()

    print("Provider Quotes:")
    quotes = {
        'Partners Life': form.recommendation.get('quote_partners_life'),
        'Fidelity Life': form.recommendation.get('quote_fidelity_life'),
        'AIA': form.recommendation.get('quote_aia'),
        'Asteron': form.recommendation.get('quote_asteron'),
        'Chubb': form.recommendation.get('quote_chubb'),
        'nib': form.recommendation.get('quote_nib')
    }
    for provider, quote in quotes.items():
        if quote:
            selected = " ← SELECTED" if provider == form.get_recommended_provider() else ""
            print(f"  {provider:15} : ${quote:,.0f}{selected}")
    print()

    lowest_provider, lowest_quote = form.get_lowest_quote()
    if lowest_provider:
        print(f"  Lowest Quote: {lowest_provider} at ${lowest_quote:,.0f}")
    print()

    # Verification
    print("VERIFICATION:")
    print("-" * 50)
    checks = [
        ("Email loaded", form.client_details.get('email'), "john.smith@email.com"),
        ("Is couple", form.is_couple(), True),
        ("Life insurance in scope", form.scope_of_advice.get('life_insurance'), True),
        ("Health insurance in scope", form.scope_of_advice.get('health_insurance'), False),
        ("Budget limitation", form.limitations.get('budget_limitations'), True),
        ("Main life cover", form.main_existing_cover.get('life_amount'), 500000.0),
        ("Partner life cover", form.partner_existing_cover.get('life_amount'), 300000.0),
        ("Selected provider", form.get_recommended_provider(), "Partners Life"),
        ("Partners Life quote", form.recommendation.get('quote_partners_life'), 850.0),
        ("Lowest quote provider", lowest_provider, "Partners Life")
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

    # Test JSON export
    print()
    print("JSON EXPORT TEST:")
    print("-" * 50)
    exported = form.to_dict()
    print(f"  Exported keys: {list(exported.keys())}")
    print(f"  String representation: {form}")

    print()
    print("=" * 70)
    if failed == 0:
        print(f"SUCCESS: All {passed} verification checks passed!")
        print("The automation form system is working correctly.")
    else:
        print(f"PARTIAL SUCCESS: {passed} passed, {failed} failed")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = test_automation_form()
    sys.exit(0 if success else 1)