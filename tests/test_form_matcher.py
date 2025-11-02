#!/usr/bin/env python3
"""
Test script for Form Matcher
Tests matching FactFinds with AutomationForms
"""
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from models.fact_find import FactFind
from models.automation_form import AutomationForm
from processors.form_matcher import FormMatcher
from processors.insurance_workflow import InsuranceWorkflow


def test_form_matcher():
    """Test the form matching system"""
    print("=" * 80)
    print("FORM MATCHER TEST")
    print("=" * 80)
    print()

    # Create fact find data
    fact_find_data = {
        "f516": "CASE-2024-001",
        "f144": "John",
        "f145": "Smith",
        "f219": "john.smith@email.com",
        "f94": "1980-05-15",
        "f6": "Software Engineer",
        "f10": "120000",
        "f8": "couple",
        "f15": "450000",
        "f16": "850000",
        # Existing insurance
        "f344": "500000",  # Life cover
        "f345": "AIA",
        "f348": "250000",  # Trauma
        "f349": "Partners Life"
    }

    # Create automation form data (matching client)
    automation_data = {
        "f3": "john.smith@email.com",  # Same email
        "f39": "couple",  # Same couple status
        # Existing cover (should match)
        "f11": "500000",  # Life amount
        "f12": "AIA",
        "f15": "250000",  # Trauma
        "f16": "Partners Life",
        # Recommendations
        "f41": "Partners Life",
        "f42": "850",
        "f5.1": "Yes",  # Life insurance
        "f5.2": "Yes"   # Income protection
    }

    # Create non-matching automation form
    other_automation_data = {
        "f3": "jane.doe@email.com",  # Different email
        "f39": "single",
        "f11": "300000",
        "f12": "Fidelity Life",
        "f41": "AIA",
        "f44": "920"
    }

    print("TEST 1: Loading Forms")
    print("-" * 60)

    # Create form matcher
    matcher = FormMatcher()

    # Load fact find
    fact_find = FactFind()
    fact_find.load_from_dict(fact_find_data)
    matcher.add_fact_find(fact_find)
    print(f"✓ Added fact find for: {fact_find.get_client_full_name()}")

    # Load matching automation form
    automation_form = AutomationForm()
    automation_form.load_from_dict(automation_data)
    matcher.add_automation_form(automation_form)
    print(f"✓ Added automation form for: {automation_form.client_details.get('email')}")

    # Load non-matching automation form
    other_form = AutomationForm()
    other_form.load_from_dict(other_automation_data)
    matcher.add_automation_form(other_form)
    print(f"✓ Added automation form for: {other_form.client_details.get('email')}")
    print()

    print(f"Matcher status: {matcher}")
    print()

    print("TEST 2: Email-Based Matching")
    print("-" * 60)

    # Test matching by email
    match_result = matcher.match_by_email("john.smith@email.com")

    if match_result:
        print(f"✓ Found match: {match_result}")
        print(f"  Confidence: {match_result.confidence:.2%}")
        print(f"  Is confident match: {match_result.is_confident_match()}")
        print(f"  Matching reasons:")
        for reason in match_result.reasons:
            print(f"    - {reason}")
    else:
        print("✗ No match found")
    print()

    print("TEST 3: Best Match Finding")
    print("-" * 60)

    # Test finding best match for automation form
    best_match = matcher.find_best_match(automation_form)

    if best_match:
        print(f"✓ Best match found: {best_match}")
        print(f"  Confidence: {best_match.confidence:.2%}")
        print(f"  Case ID: {best_match.fact_find.case_info.get('case_id')}")
        print(f"  Client: {best_match.fact_find.get_client_full_name()}")
    else:
        print("✗ No best match found")
    print()

    print("TEST 4: Non-Matching Form")
    print("-" * 60)

    # Try to match form with different email
    no_match = matcher.match_by_email("jane.doe@email.com")

    if no_match:
        print(f"  Found match (unexpected): {no_match}")
        print(f"  Confidence: {no_match.confidence:.2%}")
    else:
        print("✓ Correctly identified no match for different email")
    print()

    print("TEST 5: Workflow Integration")
    print("-" * 60)

    is_valid = False  # Initialize variable

    if match_result and match_result.is_confident_match(threshold=0.7):  # Lower threshold for test
        # Create workflow with matched forms
        workflow = InsuranceWorkflow()
        workflow.load_fact_find(fact_find_data)
        workflow.load_automation_form(automation_data)

        # Validate workflow
        is_valid, errors, warnings = workflow.validate_workflow()

        print(f"  Workflow valid: {is_valid}")
        if errors:
            print(f"  Errors: {errors}")
        if warnings:
            print(f"  Warnings: {warnings}")

        # Generate summary
        summary = workflow.get_client_summary()
        print(f"  Client: {summary['client_info'].get('name')}")
        print(f"  Recommended provider: {summary['recommendations'].get('selected_provider')}")
        print(f"  Scope: {', '.join(summary['recommendations'].get('scope_of_advice', []))}")
    else:
        print(f"  Skipping workflow test - match confidence too low or no match")
    print()

    print("TEST 6: Match Statistics")
    print("-" * 60)

    stats = matcher.get_match_statistics()
    print(f"  Total fact finds: {stats['total_fact_finds']}")
    print(f"  Total automation forms: {stats['total_automation_forms']}")
    print(f"  Total matches attempted: {stats['total_matches']}")
    print(f"  Confident matches: {stats['confident_matches']}")
    print(f"  Average confidence: {stats['average_confidence']:.2%}")
    print(f"  Unmatched fact finds: {stats['unmatched_fact_finds']}")
    print(f"  Unmatched automation forms: {stats['unmatched_automation_forms']}")
    print()

    print("TEST 7: Unmatched Forms")
    print("-" * 60)

    unmatched_fact_finds = matcher.get_unmatched_fact_finds()
    unmatched_auto_forms = matcher.get_unmatched_automation_forms()

    print(f"  Unmatched fact finds: {len(unmatched_fact_finds)}")
    for ff in unmatched_fact_finds:
        print(f"    - {ff.get_client_full_name()} ({ff.client_info.get('email')})")

    print(f"  Unmatched automation forms: {len(unmatched_auto_forms)}")
    for af in unmatched_auto_forms:
        print(f"    - {af.client_details.get('email')}")
    print()

    # Verification
    print("VERIFICATION:")
    print("-" * 60)

    checks = [
        ("Forms loaded", matcher.get_match_statistics()['total_fact_finds'] == 1, True),
        ("Automation forms loaded", matcher.get_match_statistics()['total_automation_forms'] == 2, True),
        ("Match found", match_result is not None, True),
        ("High confidence", match_result.confidence > 0.7 if match_result else False, True),
        ("Email match reason", "Email match" in str(match_result.reasons) if match_result else False, True),
        ("Case ID reason", "Case ID present" in str(match_result.reasons) if match_result else False, True),
        ("Workflow valid", is_valid if match_result else False, True),
        ("Unmatched form exists", len(unmatched_auto_forms) == 1, True)
    ]

    passed = 0
    failed = 0

    for check_name, actual, expected in checks:
        if actual == expected:
            print(f"  ✓ {check_name:30} : {actual}")
            passed += 1
        else:
            print(f"  ✗ {check_name:30} : got {actual}, expected {expected}")
            failed += 1

    # Save match history
    try:
        matcher.save_match_history("output/match_history.json")
        print()
        print("✓ Match history saved to output/match_history.json")
    except Exception as e:
        print(f"\n✗ Failed to save match history: {e}")

    print()
    print("=" * 80)
    if failed == 0:
        print(f"SUCCESS: All {passed} verification checks passed!")
        print("The form matching system is working correctly.")
    else:
        print(f"PARTIAL SUCCESS: {passed} passed, {failed} failed")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = test_form_matcher()
    sys.exit(0 if success else 1)