#!/usr/bin/env python3
"""
Test suite for Scope of Advice JSON Generator

Tests the scope_of_advice_generator module to ensure proper processing of:
- Checkbox field parsing
- In-scope/out-of-scope product determination
- Limitation reason mapping
- JSON structure generation
- Edge cases and error handling

Created: 2025-01-27
Author: Insurance SOA System
"""

import unittest
import json
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processors.scope_of_advice_generator import (
    ScopeOfAdviceGenerator,
    generate_scope_of_advice_json
)


class TestScopeOfAdviceGenerator(unittest.TestCase):
    """Test cases for the Scope of Advice Generator"""

    def setUp(self):
        """Set up test fixtures"""
        # Basic test data with all products in scope
        self.all_in_scope_data = {
            "f5": "checked",
            "f5.1": "Yes",  # Life Insurance
            "f5.2": "Yes",  # Income Protection
            "f5.3": "Yes",  # Trauma Cover
            "f5.4": "Yes",  # Health Insurance
            "f5.5": "Yes",  # TPD
            "f5.6": "Yes",  # ACC
            "f6": "",
            "f7": ""
        }

        # Mixed scope with limitations
        self.mixed_scope_data = {
            "f5": "checked",
            "f5.1": "Yes",  # Life Insurance - IN
            "f5.2": "Yes",  # Income Protection - IN
            "f5.3": "No",   # Trauma Cover - OUT
            "f5.4": "No",   # Health Insurance - OUT
            "f5.5": "Yes",  # TPD - IN
            "f5.6": "No",   # ACC - OUT
            "f6": "checked",
            "f6.1": "Yes",  # Employer medical
            "f6.3": "Yes",  # Budget limitations
            "f6.7": "Yes",  # Other
            "f7": "Client prefers to self-insure for trauma events"
        }

        # No products in scope
        self.none_in_scope_data = {
            "f5": "",
            "f5.1": "No",
            "f5.2": "No",
            "f5.3": "No",
            "f5.4": "No",
            "f5.5": "No",
            "f5.6": "No",
            "f6": "checked",
            "f6.2": "Yes",  # No debt, strong assets
            "f6.4": "Yes",  # Self-insure
            "f7": "Client has substantial assets and no debt"
        }

        # Data without 'f' prefix
        self.no_prefix_data = {
            "5": "checked",
            "5.1": "Yes",
            "5.2": "No",
            "5.3": "Yes",
            "5.4": "No",
            "5.5": "Yes",
            "5.6": "No",
            "6": "",
            "7": ""
        }

    def test_all_products_in_scope(self):
        """Test when all insurance products are in scope"""
        result = generate_scope_of_advice_json(
            self.all_in_scope_data,
            client_name="Jane Doe",
            is_couple=False
        )

        # Check structure
        self.assertIn("section_type", result)
        self.assertEqual(result["section_type"], "scope_of_advice")

        # Check processed data
        processed = result["processed_data"]
        self.assertEqual(len(processed["in_scope"]), 6)
        self.assertEqual(len(processed["out_of_scope"]), 0)
        self.assertTrue(processed["all_products_in_scope"])
        self.assertFalse(processed["has_limitations"])

    def test_mixed_scope_with_limitations(self):
        """Test mixed in-scope and out-of-scope products with limitations"""
        result = generate_scope_of_advice_json(
            self.mixed_scope_data,
            client_name="John Smith",
            is_couple=False
        )

        processed = result["processed_data"]

        # Check scope counts
        self.assertEqual(len(processed["in_scope"]), 3)
        self.assertEqual(len(processed["out_of_scope"]), 3)

        # Check in-scope products
        self.assertIn("Life Insurance", processed["in_scope"])
        self.assertIn("Income Protection", processed["in_scope"])
        self.assertIn("Total Permanent Disability (TPD)", processed["in_scope"])

        # Check out-of-scope products
        self.assertIn("Trauma Cover", processed["out_of_scope"])
        self.assertIn("Health Insurance", processed["out_of_scope"])
        self.assertIn("ACC Top-Up", processed["out_of_scope"])

        # Check limitations
        self.assertTrue(processed["has_limitations"])
        self.assertEqual(len(processed["active_limitations"]), 3)

        # Check limitation codes
        limitation_codes = [lim["code"] for lim in processed["active_limitations"]]
        self.assertIn("employer_medical", limitation_codes)
        self.assertIn("budget_limitations", limitation_codes)
        self.assertIn("other", limitation_codes)

    def test_no_products_in_scope(self):
        """Test when no products are in scope"""
        result = generate_scope_of_advice_json(
            self.none_in_scope_data,
            client_name="Bob Wilson",
            is_couple=True
        )

        processed = result["processed_data"]

        # Check all products are out of scope
        self.assertEqual(len(processed["in_scope"]), 0)
        self.assertEqual(len(processed["out_of_scope"]), 6)
        self.assertTrue(processed["no_products_in_scope"])

        # Check limitations are present
        self.assertTrue(processed["has_limitations"])
        limitation_codes = [lim["code"] for lim in processed["active_limitations"]]
        self.assertIn("no_debt_strong_assets", limitation_codes)
        self.assertIn("self_insure", limitation_codes)

        # Check context for couple
        context = result["prose_generation"]["context"]
        self.assertTrue(context["is_couple"])

    def test_field_extraction_without_prefix(self):
        """Test field extraction works without 'f' prefix"""
        result = generate_scope_of_advice_json(
            self.no_prefix_data,
            client_name="Alice Brown"
        )

        processed = result["processed_data"]

        # Should have correctly identified in-scope products
        self.assertIn("Life Insurance", processed["in_scope"])
        self.assertIn("Trauma Cover", processed["in_scope"])
        self.assertIn("Total Permanent Disability (TPD)", processed["in_scope"])

        # And out-of-scope products
        self.assertIn("Income Protection", processed["out_of_scope"])
        self.assertIn("Health Insurance", processed["out_of_scope"])
        self.assertIn("ACC Top-Up", processed["out_of_scope"])

    def test_checkbox_value_parsing(self):
        """Test various checkbox value representations"""
        test_cases = [
            {"f5.1": "Yes", "expected": True},
            {"f5.1": "yes", "expected": True},
            {"f5.1": "YES", "expected": True},
            {"f5.1": "1", "expected": True},
            {"f5.1": "true", "expected": True},
            {"f5.1": "True", "expected": True},
            {"f5.1": "checked", "expected": True},
            {"f5.1": "on", "expected": True},
            {"f5.1": "x", "expected": True},
            {"f5.1": "No", "expected": False},
            {"f5.1": "no", "expected": False},
            {"f5.1": "0", "expected": False},
            {"f5.1": "false", "expected": False},
            {"f5.1": "", "expected": False},
            {"f5.1": None, "expected": False},
        ]

        for test_case in test_cases:
            data = {"f5.1": test_case["f5.1"]}
            result = generate_scope_of_advice_json(data)

            if test_case["expected"]:
                self.assertIn("Life Insurance", result["processed_data"]["in_scope"],
                            f"Failed for value: {test_case['f5.1']}")
            else:
                self.assertIn("Life Insurance", result["processed_data"]["out_of_scope"],
                            f"Failed for value: {test_case['f5.1']}")

    def test_limitation_to_product_mapping(self):
        """Test that limitations are correctly mapped to affected products"""
        data = {
            "f5.1": "No",  # Life Insurance - OUT
            "f5.2": "Yes", # Income Protection - IN
            "f5.3": "No",  # Trauma Cover - OUT
            "f5.4": "No",  # Health Insurance - OUT
            "f5.5": "No",  # TPD - OUT
            "f5.6": "Yes", # ACC - IN
            "f6.1": "Yes", # Employer medical (affects Health Insurance)
            "f6.2": "Yes", # No debt/assets (affects Life Insurance)
            "f6.6": "Yes", # Uninsurable occupation (affects Income Protection, TPD)
        }

        result = generate_scope_of_advice_json(data)
        mapping = result["processed_data"]["limitation_product_mapping"]

        # Employer medical should map to Health Insurance (which is out of scope)
        self.assertIn("employer_medical", mapping)
        self.assertIn("Health Insurance", mapping["employer_medical"])

        # No debt/assets should map to Life Insurance (which is out of scope)
        self.assertIn("no_debt_strong_assets", mapping)
        self.assertIn("Life Insurance", mapping["no_debt_strong_assets"])

        # Uninsurable occupation should only map to TPD (out of scope), not Income Protection (in scope)
        self.assertIn("uninsurable_occupation", mapping)
        self.assertIn("Total Permanent Disability (TPD)", mapping["uninsurable_occupation"])
        # Income Protection is in scope, so shouldn't be in the mapping
        if "Income Protection" in mapping.get("uninsurable_occupation", []):
            self.fail("Income Protection should not be mapped as it's in scope")

    def test_limitation_notes_inclusion(self):
        """Test that limitation notes are properly included"""
        data = {
            "f5.1": "Yes",
            "f6.7": "Yes",  # Other limitation
            "f7": "Custom limitation reason: pre-existing medical conditions"
        }

        result = generate_scope_of_advice_json(data)

        # Check notes are in form data
        self.assertEqual(
            result["form_data"]["limitation_notes"],
            "Custom limitation reason: pre-existing medical conditions"
        )

        # Check notes are referenced in limitations content
        limitations_content = result["prose_generation"]["required_sections"]["limitations"]["suggested_content"]
        self.assertIn("Custom limitation reason", limitations_content,
                     "Limitation notes should be included in limitations section")

    def test_prose_generation_context(self):
        """Test prose generation context and required sections"""
        result = generate_scope_of_advice_json(
            self.mixed_scope_data,
            client_name="Test Client",
            is_couple=True
        )

        prose_gen = result["prose_generation"]

        # Check context
        context = prose_gen["context"]
        self.assertEqual(context["client_name"], "Test Client")
        self.assertTrue(context["is_couple"])
        self.assertEqual(context["in_scope_count"], 3)
        self.assertEqual(context["out_of_scope_count"], 3)
        self.assertEqual(context["total_products"], 6)

        # Check required sections are present
        required_sections = prose_gen["required_sections"]
        expected_sections = [
            "summary", "in_scope", "out_of_scope", "limitations", "assumptions",
            "client_priorities", "replacements", "what_is_not_covered", "next_steps", "disclosures"
        ]

        for section in expected_sections:
            self.assertIn(section, required_sections, f"Missing section: {section}")
            # Check each section has required fields
            section_data = required_sections[section]
            self.assertIn("instruction", section_data)
            self.assertIn("max_length", section_data)
            self.assertIn("suggested_content", section_data)

        # Validate max_lengths
        self.assertEqual(required_sections["summary"]["max_length"], 700)
        self.assertEqual(required_sections["next_steps"]["max_length"], 400)
        self.assertEqual(required_sections["in_scope"]["max_length"], 500)

    def test_expected_response_structure(self):
        """Test the expected response structure for LLM"""
        result = generate_scope_of_advice_json(self.mixed_scope_data)

        expected = result["expected_response"]
        self.assertEqual(expected["format"], "structured_json")
        self.assertEqual(expected["schema"], "scope_section_v1")
        self.assertIn("fields", expected)
        self.assertIn("validation_rules", expected)

        # Check all required fields are listed
        expected_fields = [
            "summary", "in_scope", "out_of_scope", "limitations", "assumptions",
            "client_priorities", "replacements", "what_is_not_covered", "next_steps", "disclosures"
        ]
        self.assertEqual(set(expected["fields"]), set(expected_fields))

        # Check validation rules
        validation = expected["validation_rules"]
        self.assertTrue(validation["all_fields_required"])
        self.assertTrue(validation["max_lengths_enforced"])

        # Check character limits
        char_limits = validation["character_limits"]
        self.assertEqual(char_limits["summary"], 700)
        self.assertEqual(char_limits["next_steps"], 400)
        for field in ["in_scope", "out_of_scope", "limitations", "assumptions",
                     "client_priorities", "replacements", "what_is_not_covered", "disclosures"]:
            self.assertEqual(char_limits[field], 500)

    def test_timestamp_generation(self):
        """Test that timestamps are properly generated"""
        result = generate_scope_of_advice_json(self.all_in_scope_data)

        self.assertIn("timestamp", result)
        # Try to parse the timestamp
        try:
            timestamp = datetime.fromisoformat(result["timestamp"])
            self.assertIsInstance(timestamp, datetime)
        except ValueError:
            self.fail("Invalid timestamp format")

    def test_empty_form_data(self):
        """Test handling of empty form data"""
        result = generate_scope_of_advice_json({})

        # Should handle gracefully with all products out of scope
        processed = result["processed_data"]
        self.assertEqual(len(processed["in_scope"]), 0)
        self.assertEqual(len(processed["out_of_scope"]), 6)  # All products out

    def test_budget_limitations_affect_all(self):
        """Test that budget limitations can affect all products"""
        data = {
            "f5.1": "No",
            "f5.2": "No",
            "f5.3": "No",
            "f5.4": "No",
            "f5.5": "No",
            "f5.6": "No",
            "f6.3": "Yes",  # Budget limitations
        }

        result = generate_scope_of_advice_json(data)
        mapping = result["processed_data"]["limitation_product_mapping"]

        # Budget limitations should map to all out-of-scope products
        if "budget_limitations" in mapping:
            self.assertEqual(len(mapping["budget_limitations"]), 6)

    def test_raw_fields_preservation(self):
        """Test that raw field values are preserved in the output"""
        result = generate_scope_of_advice_json(self.mixed_scope_data)

        raw_fields = result["form_data"]["raw_fields"]

        # Check all expected fields are present
        expected_fields = [
            "field_5", "field_5_1", "field_5_2", "field_5_3",
            "field_5_4", "field_5_5", "field_5_6", "field_6",
            "field_6_1", "field_6_2", "field_6_3", "field_6_4",
            "field_6_5", "field_6_6", "field_6_7", "field_7"
        ]

        for field in expected_fields:
            self.assertIn(field, raw_fields)

        # Check specific values are preserved
        self.assertEqual(raw_fields["field_5_1"], "Yes")
        self.assertEqual(raw_fields["field_5_3"], "No")
        self.assertEqual(raw_fields["field_6_1"], "Yes")
        self.assertEqual(raw_fields["field_7"], "Client prefers to self-insure for trauma events")


    def test_structured_content_generation(self):
        """Test that all 10 structured sections generate appropriate content"""
        # Test with comprehensive data
        data = {
            "f5.1": "Yes",  # Life Insurance
            "f5.2": "Yes",  # Income Protection
            "f5.3": "No",   # Trauma Cover
            "f5.4": "No",   # Health Insurance
            "f5.5": "Yes",  # TPD
            "f5.6": "No",   # ACC
            "f6.1": "Yes",  # Employer medical
            "f6.3": "Yes",  # Budget limitations
            "f7": "Additional context about budget constraints"
        }

        result = generate_scope_of_advice_json(data, "John Doe", False)
        sections = result["prose_generation"]["required_sections"]

        # Test summary section
        summary = sections["summary"]["suggested_content"]
        self.assertIsNotNone(summary)
        self.assertLessEqual(len(summary), 700, "Summary exceeds max length")
        self.assertIn("3 insurance product", summary)

        # Test in_scope section
        in_scope = sections["in_scope"]["suggested_content"]
        self.assertIn("Life Insurance", in_scope)
        self.assertIn("Income Protection", in_scope)
        self.assertIn("Total Permanent Disability", in_scope)
        self.assertLessEqual(len(in_scope), 500)

        # Test out_of_scope section
        out_of_scope = sections["out_of_scope"]["suggested_content"]
        self.assertIn("Trauma Cover", out_of_scope)
        self.assertIn("Health Insurance", out_of_scope)
        self.assertLessEqual(len(out_of_scope), 500)

        # Test limitations section
        limitations = sections["limitations"]["suggested_content"]
        self.assertIn("Medical cover provided through employer", limitations)
        self.assertIn("Budget", limitations)
        self.assertLessEqual(len(limitations), 500)

        # Test assumptions section
        assumptions = sections["assumptions"]["suggested_content"]
        self.assertIn("client requires protection", assumptions)
        self.assertIn("excluded products", assumptions)
        self.assertLessEqual(len(assumptions), 500)

        # Test client_priorities section
        priorities = sections["client_priorities"]["suggested_content"]
        self.assertIn("protect family", priorities)
        self.assertIn("maintain income", priorities)
        self.assertIn("budget constraints", priorities)
        self.assertLessEqual(len(priorities), 500)

        # Test replacements section
        replacements = sections["replacements"]["suggested_content"]
        self.assertIsNotNone(replacements)
        self.assertLessEqual(len(replacements), 500)

        # Test what_is_not_covered section
        not_covered = sections["what_is_not_covered"]["suggested_content"]
        self.assertIn("private medical", not_covered)
        self.assertLessEqual(len(not_covered), 500)

        # Test next_steps section
        next_steps = sections["next_steps"]["suggested_content"]
        self.assertIn("Review recommended products", next_steps)
        self.assertLessEqual(len(next_steps), 400)

        # Test disclosures section
        disclosures = sections["disclosures"]["suggested_content"]
        self.assertIn("based on information provided", disclosures)
        self.assertIn("exclusions", disclosures)
        self.assertLessEqual(len(disclosures), 500)


class TestScopeOfAdviceIntegration(unittest.TestCase):
    """Integration tests for the Scope of Advice Generator"""

    def test_complete_workflow(self):
        """Test complete workflow from raw data to final JSON"""
        # Simulate real Gravity Forms data
        gravity_forms_data = {
            "form_id": "2",
            "form_title": "Automation Form",
            "date_created": "2025-01-27",
            "f5": "Life Insurance, Income Protection, TPD",
            "f5.1": "checked",
            "f5.2": "checked",
            "f5.3": "",
            "f5.4": "",
            "f5.5": "checked",
            "f5.6": "",
            "f6": "Employer medical, Budget limitations",
            "f6.1": "x",
            "f6.2": "",
            "f6.3": "x",
            "f6.4": "",
            "f6.5": "",
            "f6.6": "",
            "f6.7": "",
            "f7": "",
            "client_email": "test@example.com",
            "adviser_name": "John Adviser"
        }

        # Generate JSON
        result = generate_scope_of_advice_json(
            gravity_forms_data,
            client_name="Test Client",
            is_couple=False
        )

        # Validate complete structure
        self.assertEqual(result["section_type"], "scope_of_advice")
        self.assertIn("form_data", result)
        self.assertIn("processed_data", result)
        self.assertIn("prose_generation", result)
        self.assertIn("expected_response", result)

        # Verify processing
        processed = result["processed_data"]
        self.assertEqual(len(processed["in_scope"]), 3)
        self.assertEqual(len(processed["out_of_scope"]), 3)
        self.assertTrue(processed["has_limitations"])

        # Verify JSON is serializable
        try:
            json_str = json.dumps(result, indent=2)
            self.assertTrue(len(json_str) > 0)
        except Exception as e:
            self.fail(f"Failed to serialize result to JSON: {e}")

    def test_real_world_scenarios(self):
        """Test various real-world scenarios"""
        scenarios = [
            {
                "name": "Young professional - basic coverage",
                "data": {
                    "f5.1": "Yes",  # Life
                    "f5.2": "Yes",  # Income Protection
                    "f5.3": "No",   # Trauma
                    "f5.4": "No",   # Health
                    "f5.5": "Yes",  # TPD
                    "f5.6": "No",   # ACC
                    "f6.3": "Yes",  # Budget limitations
                    "f6.5": "Yes",  # No dependants
                    "f7": "Starting career, limited budget"
                },
                "expected_in_scope": ["Life Insurance", "Income Protection", "Total Permanent Disability (TPD)"],
                "expected_limitations": ["budget_limitations", "no_dependants"]
            },
            {
                "name": "High net worth - self insure",
                "data": {
                    "f5.1": "No",
                    "f5.2": "No",
                    "f5.3": "No",
                    "f5.4": "No",
                    "f5.5": "No",
                    "f5.6": "No",
                    "f6.2": "Yes",  # No debt, strong assets
                    "f6.4": "Yes",  # Self-insure
                    "f7": "Client has $10M+ net worth"
                },
                "expected_in_scope": [],
                "expected_limitations": ["no_debt_strong_assets", "self_insure"]
            },
            {
                "name": "Family with employer benefits",
                "data": {
                    "f5.1": "Yes",  # Life
                    "f5.2": "Yes",  # Income Protection
                    "f5.3": "Yes",  # Trauma
                    "f5.4": "No",   # Health (employer covers)
                    "f5.5": "Yes",  # TPD
                    "f5.6": "Yes",  # ACC
                    "f6.1": "Yes",  # Employer medical
                    "f7": "Comprehensive employer health plan"
                },
                "expected_in_scope": ["Life Insurance", "Income Protection", "Trauma Cover",
                                    "Total Permanent Disability (TPD)", "ACC Top-Up"],
                "expected_limitations": ["employer_medical"]
            }
        ]

        for scenario in scenarios:
            with self.subTest(scenario=scenario["name"]):
                result = generate_scope_of_advice_json(scenario["data"])
                processed = result["processed_data"]

                # Check in-scope products
                self.assertEqual(
                    set(processed["in_scope"]),
                    set(scenario["expected_in_scope"]),
                    f"Scenario: {scenario['name']}"
                )

                # Check limitations
                limitation_codes = [lim["code"] for lim in processed["active_limitations"]]
                for expected_lim in scenario["expected_limitations"]:
                    self.assertIn(
                        expected_lim,
                        limitation_codes,
                        f"Missing limitation '{expected_lim}' in scenario: {scenario['name']}"
                    )


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestScopeOfAdviceGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestScopeOfAdviceIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success/failure
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)