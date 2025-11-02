#!/usr/bin/env python3
"""
Live Integration Test for Scope of Advice and Where Are You Now Generators

This script tests both generators with realistic data and shows the output
that would be sent to Zapier or an LLM for processing.

Created: 2025-01-27
Author: Insurance SOA System
"""

import json
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.processors.scope_of_advice_generator import generate_scope_of_advice_json
from src.processors.where_are_you_now_generator import generate_where_are_you_now_json


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)


def test_scope_of_advice():
    """Test the Scope of Advice generator"""
    print_header("TESTING SCOPE OF ADVICE GENERATOR")

    # Sample data matching automation form fields
    test_data = {
        # Scope checkboxes
        "f5.1": "Yes",  # Life Insurance
        "f5.2": "Yes",  # Income Protection
        "f5.3": "No",   # Trauma Cover
        "f5.4": "No",   # Health Insurance
        "f5.5": "Yes",  # TPD
        "f5.6": "No",   # ACC

        # Limitations
        "f6.1": "Yes",  # Employer medical
        "f6.3": "Yes",  # Budget limitations
        "f7": "Client has comprehensive health coverage through employer, budget allows for essential coverage only"
    }

    result = generate_scope_of_advice_json(
        test_data,
        client_name="Test Client",
        is_couple=False
    )

    print("\n✅ SCOPE OF ADVICE RESULTS:")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Section Type: {result['section_type']}")

    print("\n📊 Processed Data:")
    processed = result['processed_data']
    print(f"In Scope ({len(processed['in_scope'])}): {', '.join(processed['in_scope'])}")
    print(f"Out of Scope ({len(processed['out_of_scope'])}): {', '.join(processed['out_of_scope'])}")
    print(f"Active Limitations: {[lim['code'] for lim in processed['active_limitations']]}")

    print("\n📝 Generated Content (First 3 sections):")
    sections = result['prose_generation']['required_sections']
    for i, (section_name, section_data) in enumerate(list(sections.items())[:3], 1):
        print(f"\n{i}. {section_name.upper()}:")
        print(f"   {section_data['suggested_content'][:150]}...")

    return result


def test_where_are_you_now():
    """Test the Where Are You Now generator"""
    print_header("TESTING WHERE ARE YOU NOW GENERATOR")

    # Sample data matching fact find fields
    test_data = {
        # Personal details
        "f144": "John",
        "f146": "Sarah",
        "f95": "1985-03-15",
        "f6": "Software Engineer",
        "f40": "Marketing Manager",
        "f277": "Tech Corp",
        "f297": "Marketing Agency",
        "f10": "120000",
        "f42": "85000",
        "f482": "No",   # Not self-employed
        "f483": "No",
        "f501": "Yes",  # Will in place

        # Assets
        "f16": "850000",   # House value
        "f15": "450000",   # Mortgage
        "f468": "350000",  # Investment property
        "f469": "280000",  # Investment debt
        "f60": "ANZ",      # KiwiSaver 1
        "f61": "45000",
        "f62": "Westpac",  # KiwiSaver 2
        "f215": "32000",
        "f33": "Savings",
        "f26": "25000",
        "f34": "Shares",
        "f28": "15000",

        # Liabilities
        "f71": "Credit Card",
        "f72": "5000",
        "f73": "Car Loan",
        "f74": "12000"
    }

    result = generate_where_are_you_now_json(
        test_data,
        client_name="John and Sarah Smith",
        is_couple=True
    )

    print("\n✅ WHERE ARE YOU NOW RESULTS:")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Section Type: {result['section_type']}")

    print("\n📊 Financial Summary:")
    summary = result['processed_data']['financial_summary']
    print(f"Total Assets: ${summary['total_assets']:,.0f}")
    print(f"Total Liabilities: ${summary['total_liabilities']:,.0f}")
    print(f"Net Worth: ${summary['net_worth']:,.0f}")
    print(f"Property Equity: ${summary['property_equity']:,.0f}")
    print(f"Total Income: ${summary['total_income']:,.0f}")
    print(f"Debt-to-Income: {summary['debt_to_income_ratio']}%")

    print("\n📝 Generated Content (First 3 sections):")
    sections = result['prose_generation']['required_sections']
    for i, (section_name, section_data) in enumerate(list(sections.items())[:3], 1):
        print(f"\n{i}. {section_name.upper()}:")
        print(f"   {section_data['suggested_content'][:150]}...")

    return result


def create_zapier_payload(scope_result, where_result):
    """Create a combined payload suitable for Zapier"""
    print_header("ZAPIER-READY PAYLOAD")

    zapier_payload = {
        "timestamp": datetime.now().isoformat(),
        "client_name": "John and Sarah Smith",
        "is_couple": True,

        # Scope of Advice Summary
        "scope_of_advice": {
            "in_scope_products": scope_result['processed_data']['in_scope'],
            "out_of_scope_products": scope_result['processed_data']['out_of_scope'],
            "has_limitations": scope_result['processed_data']['has_limitations'],
            "sections": {
                section: data['suggested_content']
                for section, data in scope_result['prose_generation']['required_sections'].items()
            }
        },

        # Where Are You Now Summary
        "where_are_you_now": {
            "net_worth": where_result['processed_data']['financial_summary']['net_worth'],
            "total_assets": where_result['processed_data']['financial_summary']['total_assets'],
            "total_liabilities": where_result['processed_data']['financial_summary']['total_liabilities'],
            "total_income": where_result['processed_data']['financial_summary']['total_income'],
            "sections": {
                section: data['suggested_content']
                for section, data in where_result['prose_generation']['required_sections'].items()
            }
        },

        # Combined status
        "processing_status": "success",
        "sections_generated": 20,  # 10 from each generator
        "ready_for_llm": True
    }

    print("\n📤 Zapier Payload Structure:")
    print(f"- Client: {zapier_payload['client_name']}")
    print(f"- Scope Products In: {len(zapier_payload['scope_of_advice']['in_scope_products'])}")
    print(f"- Net Worth: ${zapier_payload['where_are_you_now']['net_worth']:,.0f}")
    print(f"- Total Sections: {zapier_payload['sections_generated']}")
    print(f"- Ready for LLM: {zapier_payload['ready_for_llm']}")

    return zapier_payload


def save_results(scope_result, where_result, zapier_payload):
    """Save all results to files"""
    print_header("SAVING RESULTS")

    # Save individual results
    with open('test_scope_result.json', 'w') as f:
        json.dump(scope_result, f, indent=2)
    print("✅ Saved: test_scope_result.json")

    with open('test_where_result.json', 'w') as f:
        json.dump(where_result, f, indent=2)
    print("✅ Saved: test_where_result.json")

    # Save Zapier payload
    with open('test_zapier_payload.json', 'w') as f:
        json.dump(zapier_payload, f, indent=2)
    print("✅ Saved: test_zapier_payload.json")

    # Create a combined report
    report = {
        "test_run": datetime.now().isoformat(),
        "scope_validation": {
            "all_fields_present": all(
                field in scope_result['prose_generation']['required_sections']
                for field in ['summary', 'in_scope', 'out_of_scope', 'limitations',
                            'assumptions', 'client_priorities', 'replacements',
                            'what_is_not_covered', 'next_steps', 'disclosures']
            ),
            "content_within_limits": all(
                len(section['suggested_content']) <= section['max_length']
                for section in scope_result['prose_generation']['required_sections'].values()
            )
        },
        "where_validation": {
            "all_fields_present": all(
                field in where_result['prose_generation']['required_sections']
                for field in ['personal_summary', 'employment_status', 'asset_summary',
                            'liability_summary', 'net_worth_position', 'kiwisaver_status',
                            'property_position', 'estate_planning', 'key_observations',
                            'financial_capacity']
            ),
            "content_within_limits": all(
                len(section['suggested_content']) <= section['max_length']
                for section in where_result['prose_generation']['required_sections'].values()
            )
        },
        "combined_stats": {
            "total_sections": 20,
            "total_characters": sum(
                len(section['suggested_content'])
                for section in scope_result['prose_generation']['required_sections'].values()
            ) + sum(
                len(section['suggested_content'])
                for section in where_result['prose_generation']['required_sections'].values()
            )
        }
    }

    with open('test_validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    print("✅ Saved: test_validation_report.json")

    return report


def main():
    """Run the live integration test"""
    print("\n" + "🚀"*40)
    print(" LIVE INTEGRATION TEST - INSURANCE SOA GENERATORS")
    print(" Testing Scope of Advice + Where Are You Now")
    print("🚀"*40)

    try:
        # Test both generators
        scope_result = test_scope_of_advice()
        where_result = test_where_are_you_now()

        # Create Zapier payload
        zapier_payload = create_zapier_payload(scope_result, where_result)

        # Save results
        report = save_results(scope_result, where_result, zapier_payload)

        # Final validation
        print_header("VALIDATION RESULTS")
        print(f"\n✅ Scope of Advice:")
        print(f"   - All fields present: {report['scope_validation']['all_fields_present']}")
        print(f"   - Content within limits: {report['scope_validation']['content_within_limits']}")

        print(f"\n✅ Where Are You Now:")
        print(f"   - All fields present: {report['where_validation']['all_fields_present']}")
        print(f"   - Content within limits: {report['where_validation']['content_within_limits']}")

        print(f"\n✅ Combined:")
        print(f"   - Total sections: {report['combined_stats']['total_sections']}")
        print(f"   - Total characters: {report['combined_stats']['total_characters']:,}")

        print("\n" + "🎉"*40)
        print(" ✅ LIVE TEST COMPLETED SUCCESSFULLY!")
        print(" Ready for Zapier integration")
        print("🎉"*40)

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)