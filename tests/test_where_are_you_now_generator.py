#!/usr/bin/env python3
"""
Test suite for Where Are You Now JSON Generator

Tests the where_are_you_now_generator module to ensure proper processing of:
- Personal details extraction
- Assets and liabilities parsing
- Financial calculations (net worth, equity, ratios)
- KiwiSaver aggregation
- Content generation for all 10 sections
- Edge cases and error handling

Created: 2025-01-27
Author: Insurance SOA System
"""

import unittest
import json
from datetime import datetime, date
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processors.where_are_you_now_generator import (
    WhereAreYouNowGenerator,
    generate_where_are_you_now_json
)


class TestWhereAreYouNowGenerator(unittest.TestCase):
    """Test cases for the Where Are You Now Generator"""

    def setUp(self):
        """Set up test fixtures"""
        # Comprehensive test data - couple with full financial details
        self.full_data = {
            # Personal details
            "f144": "John",
            "f146": "Jane",
            "f95": "1985-03-15",
            "f482": "No",  # Not self-employed
            "f483": "Yes",  # Partner self-employed
            "f6": "Software Engineer",
            "f40": "Marketing Consultant",
            "f277": "Tech Corp Ltd",
            "f297": "Self-Employed",
            "f10": "$120,000",
            "f42": "$85,000",
            "f501": "Yes - current",

            # Assets
            "f16": "850000",  # House value
            "f15": "450000",  # Mortgage
            "f468": "350000",  # Investment property value
            "f469": "280000",  # Investment property debt
            "f60": "ANZ",  # KiwiSaver 1
            "f61": "45000",
            "f62": "Westpac",  # KiwiSaver 2
            "f215": "32000",
            "f33": "Savings Account",
            "f26": "25000",
            "f34": "Term Deposit",
            "f28": "50000",
            "f466": "1400000",  # Asset total

            # Liabilities
            "f71": "Credit Card",
            "f72": "5000",
            "f73": "Car Loan",
            "f74": "15000"
        }

        # Minimal data - single person
        self.minimal_data = {
            "f144": "Alice",
            "f95": "1990-06-20",
            "f6": "Teacher",
            "f10": "75000",
            "f16": "0",  # No house
            "f15": "0"  # No mortgage
        }

        # High net worth data
        self.high_net_worth_data = {
            "f144": "Robert",
            "f95": "1965-01-01",
            "f6": "Company Director",
            "f10": "500000",
            "f16": "2500000",
            "f15": "0",  # No mortgage
            "f468": "5000000",  # Large property portfolio
            "f469": "1500000",
            "f61": "850000",  # Large KiwiSaver
            "f466": "10000000"  # High total assets
        }

        # Data without 'f' prefix
        self.no_prefix_data = {
            "144": "Sarah",
            "95": "1988-12-25",
            "6": "Nurse",
            "10": "68000",
            "16": "450000",
            "15": "380000"
        }

    def test_personal_details_extraction(self):
        """Test extraction of personal details"""
        result = generate_where_are_you_now_json(
            self.full_data,
            client_name="John and Jane Smith",
            is_couple=True
        )

        personal = result["form_data"]["personal_details"]

        # Check personal fields
        self.assertEqual(personal["main_first_name"], "John")
        self.assertEqual(personal["partner_first_name"], "Jane")
        self.assertEqual(personal["main_occupation"], "Software Engineer")
        self.assertEqual(personal["partner_occupation"], "Marketing Consultant")
        self.assertEqual(personal["main_annual_income"], 120000)
        self.assertEqual(personal["partner_annual_income"], 85000)

        # Check self-employed status
        self.assertFalse(personal["main_self_employed"])
        self.assertTrue(personal["partner_self_employed"])

    def test_assets_extraction(self):
        """Test extraction of assets"""
        result = generate_where_are_you_now_json(self.full_data)

        assets = result["form_data"]["assets"]

        # Check assets were extracted
        self.assertEqual(len(assets), 2)  # Savings and Term Deposit

        # Verify asset details
        self.assertEqual(assets[0]["name"], "Savings Account")
        self.assertEqual(assets[0]["value"], 25000)
        self.assertEqual(assets[1]["name"], "Term Deposit")
        self.assertEqual(assets[1]["value"], 50000)

    def test_liabilities_extraction(self):
        """Test extraction of liabilities"""
        result = generate_where_are_you_now_json(self.full_data)

        liabilities = result["form_data"]["liabilities"]

        # Check liabilities were extracted
        self.assertEqual(len(liabilities), 2)  # Credit Card and Car Loan

        # Verify liability details
        self.assertEqual(liabilities[0]["name"], "Credit Card")
        self.assertEqual(liabilities[0]["value"], 5000)
        self.assertEqual(liabilities[1]["name"], "Car Loan")
        self.assertEqual(liabilities[1]["value"], 15000)

    def test_kiwisaver_extraction(self):
        """Test extraction of KiwiSaver accounts"""
        result = generate_where_are_you_now_json(self.full_data)

        kiwisaver = result["form_data"]["kiwisaver_accounts"]

        # Check KiwiSaver accounts
        self.assertEqual(len(kiwisaver), 2)

        # Verify account details
        self.assertEqual(kiwisaver[0]["provider"], "ANZ")
        self.assertEqual(kiwisaver[0]["balance"], 45000)
        self.assertEqual(kiwisaver[1]["provider"], "Westpac")
        self.assertEqual(kiwisaver[1]["balance"], 32000)

    def test_financial_calculations(self):
        """Test financial calculations"""
        result = generate_where_are_you_now_json(self.full_data)

        summary = result["processed_data"]["financial_summary"]

        # Check calculations
        self.assertGreater(summary["total_assets"], 0)
        self.assertGreater(summary["total_liabilities"], 0)
        self.assertEqual(summary["net_worth"],
                        summary["total_assets"] - summary["total_liabilities"])

        # Check income
        self.assertEqual(summary["total_income"], 205000)  # 120k + 85k

        # Check KiwiSaver total
        self.assertEqual(summary["kiwisaver_total"], 77000)  # 45k + 32k

        # Check property equity calculation
        self.assertGreater(summary["property_equity"], 0)

        # Check debt-to-income ratio
        self.assertGreater(summary["debt_to_income_ratio"], 0)

    def test_age_calculation(self):
        """Test age calculation from date of birth"""
        result = generate_where_are_you_now_json(self.full_data)

        age = result["processed_data"]["personal_summary"]["age"]

        # Calculate expected age (born 1985-03-15)
        today = date.today()
        expected_age = today.year - 1985
        if (today.month, today.day) < (3, 15):
            expected_age -= 1

        self.assertEqual(age, expected_age)

    def test_net_worth_calculation(self):
        """Test net worth calculation"""
        result = generate_where_are_you_now_json(self.full_data)

        summary = result["processed_data"]["financial_summary"]
        breakdown = result["processed_data"]["asset_breakdown"]
        liab_breakdown = result["processed_data"]["liability_breakdown"]

        # Verify components add up correctly
        total_property = breakdown["property_value"] + breakdown["investment_properties"]
        total_debt = liab_breakdown["home_mortgage"] + liab_breakdown["investment_debt"]

        self.assertGreater(summary["net_worth"], 0)

    def test_property_equity_calculation(self):
        """Test property equity calculation"""
        result = generate_where_are_you_now_json(self.full_data)

        summary = result["processed_data"]["financial_summary"]

        # Calculate expected equity
        # Home: 850k - 450k = 400k
        # Investment: 350k - 280k = 70k
        # Total: 470k
        expected_equity = (850000 - 450000) + (350000 - 280000)

        self.assertEqual(summary["property_equity"], expected_equity)

    def test_minimal_data_handling(self):
        """Test handling of minimal data"""
        result = generate_where_are_you_now_json(
            self.minimal_data,
            client_name="Alice Brown",
            is_couple=False
        )

        # Check structure is complete
        self.assertIn("prose_generation", result)
        self.assertIn("required_sections", result["prose_generation"])
        self.assertEqual(len(result["prose_generation"]["required_sections"]), 10)

        # Check calculations with minimal data
        summary = result["processed_data"]["financial_summary"]
        self.assertEqual(summary["property_equity"], 0)
        self.assertEqual(summary["kiwisaver_total"], 0)

    def test_high_net_worth_scenario(self):
        """Test high net worth scenario"""
        result = generate_where_are_you_now_json(
            self.high_net_worth_data,
            client_name="Robert Anderson",
            is_couple=False
        )

        summary = result["processed_data"]["financial_summary"]

        # Check high values are handled correctly
        self.assertGreater(summary["total_assets"], 5000000)
        self.assertGreater(summary["net_worth"], 3000000)

        # Check description
        context = result["prose_generation"]["context"]
        self.assertIn("high", context["financial_position"].lower())

    def test_no_prefix_data(self):
        """Test data without 'f' prefix"""
        result = generate_where_are_you_now_json(self.no_prefix_data)

        personal = result["form_data"]["personal_details"]

        # Should extract fields without prefix
        self.assertEqual(personal["main_first_name"], "Sarah")
        self.assertEqual(personal["main_occupation"], "Nurse")
        self.assertEqual(personal["main_annual_income"], 68000)

    def test_currency_parsing(self):
        """Test various currency format parsing"""
        test_data = {
            "f10": "$120,000.50",
            "f16": "850000",
            "f15": "450,000",
            "f61": "$45000.00",
            "f26": "25,000.00"
        }

        result = generate_where_are_you_now_json(test_data)

        personal = result["form_data"]["personal_details"]
        self.assertEqual(personal.get("main_annual_income", 0), 120000.50)

        summary = result["processed_data"]["financial_summary"]
        self.assertGreater(summary["property_equity"], 0)

    def test_all_required_sections_present(self):
        """Test all 10 required sections are present"""
        result = generate_where_are_you_now_json(self.full_data)

        sections = result["prose_generation"]["required_sections"]

        expected_sections = [
            "personal_summary", "employment_status", "asset_summary",
            "liability_summary", "net_worth_position", "kiwisaver_status",
            "property_position", "estate_planning", "key_observations",
            "financial_capacity"
        ]

        for section in expected_sections:
            self.assertIn(section, sections)

            # Check section structure
            section_data = sections[section]
            self.assertIn("instruction", section_data)
            self.assertIn("max_length", section_data)
            self.assertIn("suggested_content", section_data)

    def test_content_length_compliance(self):
        """Test that generated content respects max lengths"""
        result = generate_where_are_you_now_json(self.full_data)

        sections = result["prose_generation"]["required_sections"]

        for section_name, section_data in sections.items():
            content = section_data["suggested_content"]
            max_length = section_data["max_length"]

            self.assertLessEqual(
                len(content), max_length,
                f"Section {section_name} exceeds max length: {len(content)} > {max_length}"
            )

    def test_estate_planning_status(self):
        """Test estate planning status processing"""
        # Test with "Yes" status
        result = generate_where_are_you_now_json(self.full_data)
        estate = result["prose_generation"]["required_sections"]["estate_planning"]["suggested_content"]
        self.assertIn("in place", estate)

        # Test with "No" status
        no_will_data = self.full_data.copy()
        no_will_data["f501"] = "No"
        result = generate_where_are_you_now_json(no_will_data)
        estate = result["prose_generation"]["required_sections"]["estate_planning"]["suggested_content"]
        self.assertIn("not in place", estate)

    def test_debt_to_income_ratio(self):
        """Test debt-to-income ratio calculation"""
        result = generate_where_are_you_now_json(self.full_data)

        summary = result["processed_data"]["financial_summary"]

        # Calculate expected ratio
        total_debt = 450000 + 280000 + 5000 + 15000  # Mortgages + other debts
        total_income = 205000
        expected_ratio = round((total_debt / total_income) * 100, 1)

        self.assertEqual(summary["debt_to_income_ratio"], expected_ratio)

    def test_multiple_assets_extraction(self):
        """Test extraction of multiple assets (up to 15)"""
        # Create data with many assets
        multi_asset_data = self.full_data.copy()
        asset_fields = [
            ("f211", "f210", "Investment Fund", "100000"),
            ("f35", "f50", "Shares", "75000"),
            ("f36", "f51", "Bonds", "50000"),
            ("f37", "f52", "Crypto", "25000"),
            ("f38", "f53", "Art Collection", "30000")
        ]

        for name_field, value_field, name, value in asset_fields:
            multi_asset_data[name_field] = name
            multi_asset_data[value_field] = value

        result = generate_where_are_you_now_json(multi_asset_data)
        assets = result["form_data"]["assets"]

        # Should extract all assets with both name and value
        self.assertGreaterEqual(len(assets), 5)

    def test_validation_rules(self):
        """Test validation rules in expected response"""
        result = generate_where_are_you_now_json(self.full_data)

        expected = result["expected_response"]

        # Check format and schema
        self.assertEqual(expected["format"], "structured_json")
        self.assertEqual(expected["schema"], "where_are_you_now_v1")

        # Check validation rules
        validation = expected["validation_rules"]
        self.assertTrue(validation["all_fields_required"])
        self.assertTrue(validation["max_lengths_enforced"])

        # Check character limits match section max_lengths
        char_limits = validation["character_limits"]
        sections = result["prose_generation"]["required_sections"]

        for section_name in sections:
            self.assertEqual(
                char_limits[section_name],
                sections[section_name]["max_length"]
            )


class TestWhereAreYouNowIntegration(unittest.TestCase):
    """Integration tests for Where Are You Now Generator"""

    def test_complete_workflow(self):
        """Test complete workflow from raw data to final JSON"""
        # Simulate comprehensive Gravity Forms data
        gravity_forms_data = {
            # Personal details
            "f144": "Michael",
            "f146": "Sarah",
            "f95": "1982-07-15",
            "f482": "checked",  # Self-employed
            "f483": "",
            "f6": "Business Owner",
            "f40": "Dentist",
            "f277": "Self",
            "f297": "Dental Clinic Ltd",
            "f10": "180000",
            "f42": "150000",
            "f501": "Yes",

            # Property
            "f16": "$1,200,000",
            "f15": "$650,000",
            "f468": "$800,000",
            "f469": "$600,000",

            # KiwiSaver
            "f60": "Simplicity",
            "f61": "$125,000",
            "f62": "Milford",
            "f215": "$95,000",
            "f217": "Fisher Funds",
            "f216": "$45,000",

            # Assets
            "f33": "Business Assets",
            "f26": "$450,000",
            "f34": "Share Portfolio",
            "f28": "$180,000",
            "f211": "Managed Funds",
            "f210": "$220,000",

            # Liabilities
            "f71": "Business Loan",
            "f72": "$120,000",
            "f73": "Vehicle Finance",
            "f74": "$45,000"
        }

        # Generate JSON
        result = generate_where_are_you_now_json(
            gravity_forms_data,
            client_name="Michael and Sarah Johnson",
            is_couple=True
        )

        # Validate complete structure
        self.assertEqual(result["section_type"], "where_are_you_now")
        self.assertIn("form_data", result)
        self.assertIn("processed_data", result)
        self.assertIn("prose_generation", result)
        self.assertIn("expected_response", result)

        # Verify financial calculations
        summary = result["processed_data"]["financial_summary"]
        self.assertGreater(summary["total_assets"], 2000000)
        self.assertGreater(summary["net_worth"], 500000)
        self.assertEqual(summary["total_income"], 330000)

        # Verify all sections have content
        sections = result["prose_generation"]["required_sections"]
        for section_name, section_data in sections.items():
            self.assertIsNotNone(section_data["suggested_content"])
            self.assertGreater(len(section_data["suggested_content"]), 20)

        # Verify JSON is serializable
        try:
            json_str = json.dumps(result, indent=2)
            self.assertTrue(len(json_str) > 0)
        except Exception as e:
            self.fail(f"Failed to serialize result to JSON: {e}")

    def test_real_world_scenarios(self):
        """Test various real-world financial scenarios"""
        scenarios = [
            {
                "name": "Young professional starting out",
                "data": {
                    "f144": "Emma",
                    "f95": "1995-08-20",
                    "f6": "Junior Doctor",
                    "f10": "85000",
                    "f16": "0",  # Renting
                    "f15": "0",
                    "f61": "12000",  # Small KiwiSaver
                    "f73": "Student Loan",
                    "f74": "45000"
                },
                "expected": {
                    "net_worth_negative": True,
                    "property_equity": 0
                }
            },
            {
                "name": "Established family",
                "data": {
                    "f144": "David",
                    "f146": "Lisa",
                    "f95": "1978-02-10",
                    "f6": "Engineer",
                    "f40": "Teacher",
                    "f10": "110000",
                    "f42": "75000",
                    "f16": "750000",
                    "f15": "400000",
                    "f61": "85000",
                    "f215": "65000",
                    "f501": "Yes"
                },
                "expected": {
                    "net_worth_positive": True,
                    "property_equity": 350000,
                    "total_income": 185000
                }
            },
            {
                "name": "Retiree",
                "data": {
                    "f144": "George",
                    "f95": "1958-11-05",
                    "f6": "Retired",
                    "f10": "45000",  # Pension
                    "f16": "950000",
                    "f15": "0",  # Paid off
                    "f61": "380000",  # Large KiwiSaver
                    "f33": "Investment Portfolio",
                    "f26": "650000"
                },
                "expected": {
                    "high_net_worth": True,
                    "debt_free": True
                }
            }
        ]

        for scenario in scenarios:
            with self.subTest(scenario=scenario["name"]):
                result = generate_where_are_you_now_json(scenario["data"])
                summary = result["processed_data"]["financial_summary"]

                if "net_worth_negative" in scenario["expected"]:
                    if scenario["expected"]["net_worth_negative"]:
                        self.assertLess(summary["net_worth"], 0,
                                      f"Scenario: {scenario['name']}")

                if "net_worth_positive" in scenario["expected"]:
                    if scenario["expected"]["net_worth_positive"]:
                        self.assertGreater(summary["net_worth"], 0,
                                         f"Scenario: {scenario['name']}")

                if "property_equity" in scenario["expected"]:
                    self.assertEqual(summary["property_equity"],
                                   scenario["expected"]["property_equity"],
                                   f"Scenario: {scenario['name']}")

                if "total_income" in scenario["expected"]:
                    self.assertEqual(summary["total_income"],
                                   scenario["expected"]["total_income"],
                                   f"Scenario: {scenario['name']}")

                if "high_net_worth" in scenario["expected"]:
                    if scenario["expected"]["high_net_worth"]:
                        self.assertGreater(summary["net_worth"], 1000000,
                                         f"Scenario: {scenario['name']}")

                if "debt_free" in scenario["expected"]:
                    if scenario["expected"]["debt_free"]:
                        self.assertEqual(summary["total_liabilities"], 0,
                                        f"Scenario: {scenario['name']}")


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestWhereAreYouNowGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestWhereAreYouNowIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success/failure
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)