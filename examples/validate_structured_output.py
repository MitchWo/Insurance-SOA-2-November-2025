#!/usr/bin/env python3
"""
Validation Script for Structured Scope of Advice Output

This script validates that the scope_of_advice_generator produces
output that meets all requirements for the 10 discrete sections.

Created: 2025-01-27
Author: Insurance SOA System
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processors.scope_of_advice_generator import generate_scope_of_advice_json


def validate_structured_output(json_output):
    """
    Validate that the JSON output meets all structured requirements

    Returns: (is_valid, errors_list)
    """
    errors = []

    # Check main structure
    if "prose_generation" not in json_output:
        errors.append("Missing 'prose_generation' section")
        return False, errors

    if "expected_response" not in json_output:
        errors.append("Missing 'expected_response' section")
        return False, errors

    # Validate prose_generation structure
    prose_gen = json_output["prose_generation"]

    if "required_sections" not in prose_gen:
        errors.append("Missing 'required_sections' in prose_generation")
    else:
        # Check all 10 sections exist
        required_sections = [
            "summary", "in_scope", "out_of_scope", "limitations", "assumptions",
            "client_priorities", "replacements", "what_is_not_covered", "next_steps", "disclosures"
        ]

        sections = prose_gen["required_sections"]

        for section_name in required_sections:
            if section_name not in sections:
                errors.append(f"Missing required section: {section_name}")
            else:
                section = sections[section_name]

                # Validate section structure
                if "instruction" not in section:
                    errors.append(f"Section '{section_name}' missing 'instruction'")

                if "max_length" not in section:
                    errors.append(f"Section '{section_name}' missing 'max_length'")

                if "suggested_content" not in section:
                    errors.append(f"Section '{section_name}' missing 'suggested_content'")
                else:
                    # Validate content length
                    content = section["suggested_content"]
                    max_length = section.get("max_length", 0)

                    if len(content) > max_length:
                        errors.append(f"Section '{section_name}' content exceeds max_length: {len(content)} > {max_length}")

        # Validate max_length values
        expected_lengths = {
            "summary": 700,
            "in_scope": 500,
            "out_of_scope": 500,
            "limitations": 500,
            "assumptions": 500,
            "client_priorities": 500,
            "replacements": 500,
            "what_is_not_covered": 500,
            "next_steps": 400,
            "disclosures": 500
        }

        for section_name, expected_length in expected_lengths.items():
            if section_name in sections:
                actual_length = sections[section_name].get("max_length", 0)
                if actual_length != expected_length:
                    errors.append(f"Section '{section_name}' has incorrect max_length: {actual_length} != {expected_length}")

    # Validate expected_response structure
    expected_resp = json_output["expected_response"]

    if expected_resp.get("format") != "structured_json":
        errors.append(f"Expected format 'structured_json', got '{expected_resp.get('format')}'")

    if expected_resp.get("schema") != "scope_section_v1":
        errors.append(f"Expected schema 'scope_section_v1', got '{expected_resp.get('schema')}'")

    if "fields" not in expected_resp:
        errors.append("Missing 'fields' in expected_response")
    else:
        expected_fields = [
            "summary", "in_scope", "out_of_scope", "limitations", "assumptions",
            "client_priorities", "replacements", "what_is_not_covered", "next_steps", "disclosures"
        ]

        if set(expected_resp["fields"]) != set(expected_fields):
            errors.append(f"Field list mismatch. Expected: {expected_fields}, Got: {expected_resp['fields']}")

    # Validate validation_rules
    if "validation_rules" not in expected_resp:
        errors.append("Missing 'validation_rules' in expected_response")
    else:
        rules = expected_resp["validation_rules"]

        if not rules.get("all_fields_required"):
            errors.append("validation_rules.all_fields_required should be True")

        if not rules.get("max_lengths_enforced"):
            errors.append("validation_rules.max_lengths_enforced should be True")

        if "character_limits" not in rules:
            errors.append("Missing 'character_limits' in validation_rules")
        else:
            char_limits = rules["character_limits"]
            expected_limits = {
                "summary": 700,
                "in_scope": 500,
                "out_of_scope": 500,
                "limitations": 500,
                "assumptions": 500,
                "client_priorities": 500,
                "replacements": 500,
                "what_is_not_covered": 500,
                "next_steps": 400,
                "disclosures": 500
            }

            for field, expected_limit in expected_limits.items():
                if field not in char_limits:
                    errors.append(f"Missing character limit for field: {field}")
                elif char_limits[field] != expected_limit:
                    errors.append(f"Incorrect character limit for {field}: {char_limits[field]} != {expected_limit}")

    is_valid = len(errors) == 0
    return is_valid, errors


def test_scenarios():
    """Test various scenarios and validate output"""

    test_cases = [
        {
            "name": "All products in scope",
            "data": {
                "f5.1": "Yes", "f5.2": "Yes", "f5.3": "Yes",
                "f5.4": "Yes", "f5.5": "Yes", "f5.6": "Yes"
            }
        },
        {
            "name": "No products in scope",
            "data": {
                "f5.1": "No", "f5.2": "No", "f5.3": "No",
                "f5.4": "No", "f5.5": "No", "f5.6": "No"
            }
        },
        {
            "name": "Mixed with limitations",
            "data": {
                "f5.1": "Yes", "f5.2": "Yes", "f5.3": "No",
                "f5.4": "No", "f5.5": "Yes", "f5.6": "No",
                "f6.1": "Yes", "f6.3": "Yes",
                "f7": "Test limitation notes"
            }
        }
    ]

    print("STRUCTURED OUTPUT VALIDATION")
    print("=" * 60)

    all_passed = True

    for test_case in test_cases:
        print(f"\nScenario: {test_case['name']}")
        print("-" * 40)

        # Generate output
        result = generate_scope_of_advice_json(
            test_case["data"],
            client_name="Test Client",
            is_couple=False
        )

        # Validate
        is_valid, errors = validate_structured_output(result)

        if is_valid:
            print("✓ PASSED - All validation checks passed")
        else:
            print("✗ FAILED - Validation errors found:")
            for error in errors:
                print(f"  - {error}")
            all_passed = False

        # Show section content lengths
        if "prose_generation" in result and "required_sections" in result["prose_generation"]:
            print("\nSection Content Lengths:")
            sections = result["prose_generation"]["required_sections"]
            for section_name, section_data in sections.items():
                content_len = len(section_data.get("suggested_content", ""))
                max_len = section_data.get("max_length", 0)
                status = "✓" if content_len <= max_len else "✗"
                print(f"  {status} {section_name}: {content_len}/{max_len} chars")

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL SCENARIOS PASSED VALIDATION")
    else:
        print("✗ SOME SCENARIOS FAILED VALIDATION")

    return all_passed


def main():
    """Main validation runner"""
    print("\n")

    # Test all scenarios
    success = test_scenarios()

    # Load and validate saved sample
    print("\n" + "=" * 60)
    print("VALIDATING SAVED SAMPLE OUTPUT")
    print("-" * 60)

    sample_file = "scope_of_advice_sample_output.json"

    if os.path.exists(sample_file):
        with open(sample_file, 'r') as f:
            sample_data = json.load(f)

        is_valid, errors = validate_structured_output(sample_data)

        if is_valid:
            print(f"✓ {sample_file} passed all validation checks")
        else:
            print(f"✗ {sample_file} has validation errors:")
            for error in errors:
                print(f"  - {error}")
    else:
        print(f"Sample file not found: {sample_file}")

    print("\n" + "=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())