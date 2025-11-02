#!/usr/bin/env python3
"""
Example Usage of Where Are You Now Generator

This script demonstrates various use cases for generating "Where Are You Now" JSON structures
from insurance fact find form data. It shows how to:
1. Process personal and financial information
2. Calculate net worth, equity, and ratios
3. Generate content for all 10 sections
4. Handle different financial scenarios
5. Integrate with LLM for prose generation

Created: 2025-01-27
Author: Insurance SOA System
"""

import json
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processors.where_are_you_now_generator import generate_where_are_you_now_json


def print_section_header(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.0f}"


def example_1_young_professional():
    """Example 1: Young professional starting career"""
    print_section_header("EXAMPLE 1: Young Professional")

    print("\nScenario: 28-year-old software developer, single, renting, building wealth")

    form_data = {
        "f144": "Alex",
        "f95": "1995-06-15",
        "f6": "Software Developer",
        "f277": "Tech Startup Inc",
        "f10": "95000",
        "f482": "No",  # Not self-employed
        "f501": "No",  # No will yet

        # No property yet (renting)
        "f16": "0",
        "f15": "0",

        # KiwiSaver
        "f60": "Simplicity",
        "f61": "28000",

        # Assets
        "f33": "Emergency Fund",
        "f26": "15000",
        "f34": "Crypto Holdings",
        "f28": "8000",

        # Liabilities
        "f71": "Student Loan",
        "f72": "35000",
        "f73": "Car Loan",
        "f74": "12000"
    }

    result = generate_where_are_you_now_json(
        form_data,
        client_name="Alex Thompson",
        is_couple=False
    )

    print("\n--- Personal Summary ---")
    personal = result["processed_data"]["personal_summary"]
    print(f"Age: {personal['age']} years old")
    print(f"Occupation: {personal['main_occupation']}")
    print(f"Employer: {personal['main_employer']}")
    print(f"Self-employed: {personal['main_self_employed']}")

    print("\n--- Financial Summary ---")
    summary = result["processed_data"]["financial_summary"]
    print(f"Total Assets: {format_currency(summary['total_assets'])}")
    print(f"Total Liabilities: {format_currency(summary['total_liabilities'])}")
    print(f"Net Worth: {format_currency(summary['net_worth'])}")
    print(f"Annual Income: {format_currency(summary['total_income'])}")
    print(f"Debt-to-Income Ratio: {summary['debt_to_income_ratio']}%")
    print(f"KiwiSaver Balance: {format_currency(summary['kiwisaver_total'])}")

    print("\n--- Generated Content Preview ---")
    sections = result["prose_generation"]["required_sections"]
    print(f"Personal Summary: {sections['personal_summary']['suggested_content'][:150]}...")
    print(f"Financial Capacity: {sections['financial_capacity']['suggested_content'][:150]}...")


def example_2_established_family():
    """Example 2: Established family with mortgage"""
    print_section_header("EXAMPLE 2: Established Family")

    print("\nScenario: Couple in their 40s, two children, home owners with mortgage")

    form_data = {
        # Personal details
        "f144": "David",
        "f146": "Sarah",
        "f95": "1982-03-20",
        "f482": "No",
        "f483": "Yes",  # Partner self-employed
        "f6": "Project Manager",
        "f40": "Physiotherapist",
        "f277": "Construction Corp",
        "f297": "Self-employed",
        "f10": "$125,000",
        "f42": "$85,000",
        "f501": "Yes - updated 2023",

        # Property
        "f16": "950000",  # House value
        "f15": "520000",  # Mortgage

        # KiwiSaver
        "f60": "ANZ",
        "f61": "95000",
        "f62": "ASB",
        "f215": "72000",

        # Assets
        "f33": "Joint Savings",
        "f26": "45000",
        "f34": "Share Portfolio",
        "f28": "38000",
        "f211": "Term Deposits",
        "f210": "50000",

        # Liabilities
        "f71": "Credit Cards",
        "f72": "8000",
        "f73": "Personal Loan",
        "f74": "15000"
    }

    result = generate_where_are_you_now_json(
        form_data,
        client_name="David and Sarah Mitchell",
        is_couple=True
    )

    print("\n--- Household Financial Position ---")
    summary = result["processed_data"]["financial_summary"]
    print(f"Combined Income: {format_currency(summary['total_income'])}")
    print(f"Total Assets: {format_currency(summary['total_assets'])}")
    print(f"Total Liabilities: {format_currency(summary['total_liabilities'])}")
    print(f"Net Worth: {format_currency(summary['net_worth'])}")
    print(f"Property Equity: {format_currency(summary['property_equity'])}")

    print("\n--- Asset Breakdown ---")
    assets = result["processed_data"]["asset_breakdown"]
    print(f"Home Value: {format_currency(assets['property_value'])}")
    print(f"KiwiSaver (both): {format_currency(assets['kiwisaver'])}")
    print(f"Other Assets: {format_currency(assets['other_assets'])}")

    print("\n--- Key Observations ---")
    observations = result["prose_generation"]["required_sections"]["key_observations"]["suggested_content"]
    print(observations)


def example_3_high_net_worth():
    """Example 3: High net worth individual with investment properties"""
    print_section_header("EXAMPLE 3: High Net Worth Individual")

    print("\nScenario: Business owner, 55 years old, multiple properties, substantial assets")

    form_data = {
        "f144": "Richard",
        "f95": "1969-01-15",
        "f6": "Company Director",
        "f277": "Own Business",
        "f10": "450000",
        "f482": "Yes",  # Self-employed
        "f501": "Yes - Family Trust established",

        # Primary residence
        "f16": "2800000",
        "f15": "0",  # No mortgage on home

        # Investment properties
        "f468": "4500000",  # Total investment property value
        "f469": "2200000",  # Investment property debt

        # KiwiSaver
        "f60": "Milford",
        "f61": "650000",

        # Multiple assets
        "f33": "Business Equity",
        "f26": "1800000",
        "f34": "Managed Funds",
        "f28": "850000",
        "f211": "Share Portfolio",
        "f210": "620000",
        "f35": "Bonds",
        "f50": "400000",
        "f36": "Gold/Commodities",
        "f51": "180000",

        # Liabilities
        "f71": "Business Loan",
        "f72": "450000"
    }

    result = generate_where_are_you_now_json(
        form_data,
        client_name="Richard Wellington",
        is_couple=False
    )

    print("\n--- Wealth Summary ---")
    summary = result["processed_data"]["financial_summary"]
    print(f"Total Assets: {format_currency(summary['total_assets'])}")
    print(f"Total Liabilities: {format_currency(summary['total_liabilities'])}")
    print(f"Net Worth: {format_currency(summary['net_worth'])}")
    print(f"Property Equity: {format_currency(summary['property_equity'])}")

    print("\n--- Property Portfolio ---")
    property_content = result["prose_generation"]["required_sections"]["property_position"]["suggested_content"]
    print(property_content)

    print("\n--- Financial Capacity for Insurance ---")
    capacity = result["prose_generation"]["required_sections"]["financial_capacity"]["suggested_content"]
    print(capacity)


def example_4_pre_retirement():
    """Example 4: Pre-retirement couple"""
    print_section_header("EXAMPLE 4: Pre-Retirement Couple")

    print("\nScenario: Couple approaching retirement, downsizing, focusing on wealth preservation")

    form_data = {
        "f144": "Robert",
        "f146": "Margaret",
        "f95": "1963-08-10",
        "f6": "Senior Consultant",
        "f40": "Part-time Teacher",
        "f10": "145000",
        "f42": "45000",
        "f501": "Yes - reviewed annually",

        # Downsized home
        "f16": "850000",
        "f15": "0",  # Paid off

        # Investment property
        "f468": "650000",
        "f469": "0",  # Also paid off

        # Large KiwiSaver balances
        "f60": "Fisher Funds",
        "f61": "485000",
        "f62": "Simplicity",
        "f215": "395000",

        # Conservative assets
        "f33": "Term Deposits",
        "f26": "250000",
        "f34": "Conservative Funds",
        "f28": "380000",
        "f211": "Cash Savings",
        "f210": "120000"
    }

    result = generate_where_are_you_now_json(
        form_data,
        client_name="Robert and Margaret Anderson",
        is_couple=True
    )

    print("\n--- Retirement Readiness ---")
    summary = result["processed_data"]["financial_summary"]
    print(f"Net Worth: {format_currency(summary['net_worth'])}")
    print(f"Total KiwiSaver: {format_currency(summary['kiwisaver_total'])}")
    print(f"Property Equity: {format_currency(summary['property_equity'])}")
    print(f"Debt-to-Income: {summary['debt_to_income_ratio']}%")

    print("\n--- Estate Planning Status ---")
    estate = result["prose_generation"]["required_sections"]["estate_planning"]["suggested_content"]
    print(estate)

    print("\n--- Net Worth Position ---")
    net_worth = result["prose_generation"]["required_sections"]["net_worth_position"]["suggested_content"]
    print(net_worth)


def example_5_complex_finances():
    """Example 5: Complex financial situation with multiple income streams"""
    print_section_header("EXAMPLE 5: Complex Financial Situation")

    print("\nScenario: Couple with business, rentals, and complex asset structure")

    form_data = {
        "f144": "James",
        "f146": "Emma",
        "f95": "1978-11-25",
        "f482": "Yes",  # Both self-employed
        "f483": "Yes",
        "f6": "Business Owner - Import/Export",
        "f40": "Business Owner - Consulting",
        "f10": "280000",
        "f42": "165000",
        "f501": "Yes - Trust structure",

        # Properties
        "f16": "1650000",
        "f15": "780000",
        "f468": "3200000",  # Multiple rentals
        "f469": "2400000",

        # KiwiSaver
        "f60": "Booster",
        "f61": "125000",
        "f62": "Generate",
        "f215": "98000",
        "f217": "Kiwi Wealth",
        "f216": "67000",  # Third account

        # Diverse assets
        "f33": "Business Value",
        "f26": "950000",
        "f34": "Commercial Property",
        "f28": "1200000",
        "f211": "Cryptocurrency",
        "f210": "85000",
        "f35": "Precious Metals",
        "f50": "120000",
        "f36": "Art Collection",
        "f51": "65000",
        "f37": "Classic Cars",
        "f52": "145000",
        "f38": "Wine Collection",
        "f53": "35000",

        # Multiple liabilities
        "f71": "Business Overdraft",
        "f72": "185000",
        "f73": "Equipment Finance",
        "f74": "92000",
        "f75": "Trade Credit",
        "f77": "67000",
        "f78": "Personal Loan",
        "f88": "45000",
        "f89": "Credit Cards",
        "f90": "22000"
    }

    result = generate_where_are_you_now_json(
        form_data,
        client_name="James and Emma Richardson",
        is_couple=True
    )

    print("\n--- Complex Asset Structure ---")
    assets = result["form_data"]["assets"]
    print(f"Number of asset categories: {len(assets)}")
    for asset in assets[:5]:
        print(f"  • {asset['name']}: {format_currency(asset['value'])}")
    if len(assets) > 5:
        print(f"  ... and {len(assets) - 5} more")

    print("\n--- Liability Structure ---")
    liabilities = result["form_data"]["liabilities"]
    print(f"Number of liabilities: {len(liabilities)}")
    total_business_debt = sum(l['value'] for l in liabilities if 'business' in l['name'].lower())
    total_personal_debt = sum(l['value'] for l in liabilities if 'business' not in l['name'].lower())
    print(f"Business-related debt: {format_currency(total_business_debt)}")
    print(f"Personal debt: {format_currency(total_personal_debt)}")

    print("\n--- Financial Metrics ---")
    summary = result["processed_data"]["financial_summary"]
    print(f"Total Assets: {format_currency(summary['total_assets'])}")
    print(f"Total Liabilities: {format_currency(summary['total_liabilities'])}")
    print(f"Net Worth: {format_currency(summary['net_worth'])}")
    print(f"Debt-to-Income: {summary['debt_to_income_ratio']}%")

    # Show asset summary section
    print("\n--- Asset Summary Content ---")
    asset_summary = result["prose_generation"]["required_sections"]["asset_summary"]["suggested_content"]
    print(asset_summary)


def example_6_debt_situation():
    """Example 6: High debt situation requiring careful analysis"""
    print_section_header("EXAMPLE 6: High Debt Situation")

    print("\nScenario: Recently divorced, rebuilding finances, significant debt")

    form_data = {
        "f144": "Michelle",
        "f95": "1985-04-12",
        "f6": "Marketing Manager",
        "f277": "Digital Agency",
        "f10": "78000",
        "f482": "No",
        "f501": "No - needs updating",

        # Lost home in divorce, renting now
        "f16": "0",
        "f15": "0",

        # Limited assets
        "f60": "Default KiwiSaver",
        "f61": "18000",
        "f33": "Emergency Savings",
        "f26": "3500",

        # Significant debts
        "f71": "Divorce Settlement Loan",
        "f72": "85000",
        "f73": "Credit Card Debt",
        "f74": "22000",
        "f75": "Personal Loan",
        "f77": "15000",
        "f78": "Car Finance",
        "f88": "28000"
    }

    result = generate_where_are_you_now_json(
        form_data,
        client_name="Michelle Roberts",
        is_couple=False
    )

    print("\n--- Current Financial Challenge ---")
    summary = result["processed_data"]["financial_summary"]
    print(f"Annual Income: {format_currency(summary['total_income'])}")
    print(f"Total Debt: {format_currency(summary['total_liabilities'])}")
    print(f"Net Worth: {format_currency(summary['net_worth'])}")
    print(f"Debt-to-Income Ratio: {summary['debt_to_income_ratio']}%")

    print("\n--- Liability Breakdown ---")
    breakdown = result["processed_data"]["liability_breakdown"]
    for liability in result["form_data"]["liabilities"]:
        print(f"  • {liability['name']}: {format_currency(liability['value'])}")

    print("\n--- Financial Capacity Assessment ---")
    capacity = result["prose_generation"]["required_sections"]["financial_capacity"]["suggested_content"]
    print(capacity)

    print("\n--- Key Observations ---")
    observations = result["prose_generation"]["required_sections"]["key_observations"]["suggested_content"]
    print(observations)


def example_7_structured_output_demo():
    """Example 7: Demonstrate structured output for LLM"""
    print_section_header("EXAMPLE 7: Structured Output for LLM")

    print("\nDemonstrating the 10 structured sections with character limits")

    form_data = {
        "f144": "Sample",
        "f95": "1980-01-01",
        "f6": "Professional",
        "f10": "100000",
        "f16": "500000",
        "f15": "300000",
        "f61": "50000",
        "f33": "Savings",
        "f26": "25000",
        "f71": "Loan",
        "f72": "20000"
    }

    result = generate_where_are_you_now_json(form_data)

    print("\n--- 10 REQUIRED SECTIONS ---")
    sections = result["prose_generation"]["required_sections"]

    for i, (section_name, section_data) in enumerate(sections.items(), 1):
        print(f"\n{i}. {section_name.upper().replace('_', ' ')}")
        print(f"   Max Length: {section_data['max_length']} characters")
        print(f"   Instruction: {section_data['instruction']}")
        content = section_data['suggested_content']
        print(f"   Content Length: {len(content)} chars")
        print(f"   Content: {content[:100]}..." if len(content) > 100 else f"   Content: {content}")

    print("\n--- VALIDATION RULES ---")
    validation = result["expected_response"]["validation_rules"]
    print(json.dumps(validation, indent=2))

    print("\n--- EXPECTED JSON OUTPUT FORMAT ---")
    print("The LLM should return exactly these fields:")
    print(json.dumps(result["expected_response"]["fields"], indent=2))


def example_8_llm_integration():
    """Example 8: Complete LLM integration example"""
    print_section_header("EXAMPLE 8: LLM Integration Template")

    form_data = {
        "f144": "John",
        "f146": "Mary",
        "f95": "1975-05-20",
        "f6": "Engineer",
        "f40": "Nurse",
        "f10": "115000",
        "f42": "72000",
        "f16": "780000",
        "f15": "420000",
        "f61": "95000",
        "f215": "68000",
        "f501": "Yes"
    }

    result = generate_where_are_you_now_json(
        form_data,
        client_name="John and Mary Peterson",
        is_couple=True
    )

    print("\n--- LLM PROMPT TEMPLATE ---")

    sections = result["prose_generation"]["required_sections"]
    context = result["prose_generation"]["context"]
    summary = result["processed_data"]["financial_summary"]

    llm_prompt = f"""
Generate the "Where Are You Now" section for an insurance Statement of Advice.

CLIENT CONTEXT:
- Name: {context['client_name']}
- Age Group: {context['age_description']}
- Financial Position: {context['financial_position']}
- Income Level: {context['income_level']}
- Is Couple: {context['is_couple']}

FINANCIAL METRICS:
- Total Assets: ${summary['total_assets']:,.0f}
- Total Liabilities: ${summary['total_liabilities']:,.0f}
- Net Worth: ${summary['net_worth']:,.0f}
- Annual Income: ${summary['total_income']:,.0f}
- Debt-to-Income Ratio: {summary['debt_to_income_ratio']}%
- Property Equity: ${summary['property_equity']:,.0f}
- KiwiSaver Total: ${summary['kiwisaver_total']:,.0f}

REQUIREMENTS:
Generate a JSON response with EXACTLY these 10 fields, respecting character limits:

{json.dumps({
    field: {
        "instruction": sections[field]["instruction"],
        "max_length": sections[field]["max_length"]
    }
    for field in result["expected_response"]["fields"]
}, indent=2)}

RESPONSE FORMAT:
{{
    "personal_summary": "...",
    "employment_status": "...",
    "asset_summary": "...",
    "liability_summary": "...",
    "net_worth_position": "...",
    "kiwisaver_status": "...",
    "property_position": "...",
    "estate_planning": "...",
    "key_observations": "...",
    "financial_capacity": "..."
}}

Use the following as guidance but personalize for this client:
{json.dumps({
    field: sections[field]["suggested_content"][:100] + "..."
    for field in list(result["expected_response"]["fields"])[:3]
}, indent=2)}
"""

    print(llm_prompt)


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print(" WHERE ARE YOU NOW GENERATOR - EXAMPLE USAGE")
    print(" Demonstrating financial analysis and report generation")
    print("="*80)

    examples = [
        ("Young Professional", example_1_young_professional),
        ("Established Family", example_2_established_family),
        ("High Net Worth", example_3_high_net_worth),
        ("Pre-Retirement", example_4_pre_retirement),
        ("Complex Finances", example_5_complex_finances),
        ("High Debt Situation", example_6_debt_situation),
        ("Structured Output Demo", example_7_structured_output_demo),
        ("LLM Integration", example_8_llm_integration)
    ]

    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning all examples...\n")

    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\nError in {name}: {e}")

    print("\n" + "="*80)
    print(" All examples completed successfully!")
    print("="*80)

    # Save a sample output for reference
    print("\n--- Saving Sample Output ---")
    sample_data = {
        "f144": "Sample Client",
        "f95": "1985-01-01",
        "f6": "Manager",
        "f10": "95000",
        "f16": "650000",
        "f15": "400000",
        "f61": "55000",
        "f33": "Savings",
        "f26": "30000",
        "f501": "Yes"
    }

    result = generate_where_are_you_now_json(
        sample_data,
        client_name="Sample Client",
        is_couple=False
    )

    output_file = "where_are_you_now_sample_output.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Sample output saved to: {output_file}")
    print(f"File contains complete JSON structure ({len(json.dumps(result))} bytes)")


if __name__ == "__main__":
    main()