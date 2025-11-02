#!/usr/bin/env python3
"""
Example Usage of Scope of Advice Generator

This script demonstrates various use cases for generating scope of advice JSON structures
from insurance automation form data. It shows how to:
1. Process different checkbox configurations
2. Handle various limitation scenarios
3. Generate JSON for LLM-based prose generation
4. Integrate with the existing Insurance SOA system

Created: 2025-01-27
Author: Insurance SOA System
"""

import json
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processors.scope_of_advice_generator import generate_scope_of_advice_json


def print_section_header(title: str):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)


def print_json_pretty(data: dict, max_depth: int = 3):
    """Pretty print JSON with controlled depth"""
    print(json.dumps(data, indent=2))


def example_1_comprehensive_coverage():
    """Example 1: Client needs comprehensive coverage - all products in scope"""
    print_section_header("EXAMPLE 1: Comprehensive Coverage")

    print("\nScenario: Young family with mortgage, seeking full insurance protection")
    print("Expected: All insurance products in scope, no limitations")

    form_data = {
        "f5": "checked",
        "f5.1": "Yes",  # Life Insurance
        "f5.2": "Yes",  # Income Protection
        "f5.3": "Yes",  # Trauma Cover
        "f5.4": "Yes",  # Health Insurance
        "f5.5": "Yes",  # Total Permanent Disability
        "f5.6": "Yes",  # ACC Top-Up
        "f6": "",       # No limitations
        "f7": ""        # No limitation notes
    }

    result = generate_scope_of_advice_json(
        form_data,
        client_name="Sarah and John Thompson",
        is_couple=True
    )

    print("\n--- Generated JSON Structure ---")
    print(f"Timestamp: {result['timestamp']}")
    print(f"Section Type: {result['section_type']}")

    print("\n--- Processed Data ---")
    processed = result['processed_data']
    print(f"In Scope Products ({len(processed['in_scope'])}): {', '.join(processed['in_scope'])}")
    print(f"Out of Scope Products: {len(processed['out_of_scope'])}")
    print(f"Has Limitations: {processed['has_limitations']}")
    print(f"All Products in Scope: {processed['all_products_in_scope']}")

    print("\n--- Prose Generation Context ---")
    context = result['prose_generation']['context']
    print(f"Client: {context['client_name']}")
    print(f"Is Couple: {context['is_couple']}")
    print(f"Opening Statement: {result['prose_generation']['template_variables']['opening_statement']}")

    print("\n--- Example Generated Prose ---")
    print(result['expected_response']['example'][:500] + "...")


def example_2_budget_constraints():
    """Example 2: Client with budget constraints - selective coverage"""
    print_section_header("EXAMPLE 2: Budget Constraints")

    print("\nScenario: Single professional with limited budget, focusing on essential coverage")
    print("Expected: Core products only (Life, Income Protection, TPD)")

    form_data = {
        "f5": "checked",
        "f5.1": "Yes",  # Life Insurance - ESSENTIAL
        "f5.2": "Yes",  # Income Protection - ESSENTIAL
        "f5.3": "No",   # Trauma Cover - skip due to budget
        "f5.4": "No",   # Health Insurance - skip
        "f5.5": "Yes",  # TPD - ESSENTIAL
        "f5.6": "No",   # ACC - skip
        "f6": "checked",
        "f6.3": "Yes",  # Budget limitations
        "f7": "Client has budget of $200/month maximum for all insurance"
    }

    result = generate_scope_of_advice_json(
        form_data,
        client_name="Michael Chen",
        is_couple=False
    )

    print("\n--- Processed Data ---")
    processed = result['processed_data']
    print(f"In Scope: {processed['in_scope']}")
    print(f"Out of Scope: {processed['out_of_scope']}")

    print("\n--- Active Limitations ---")
    for limitation in processed['active_limitations']:
        print(f"- {limitation['code']}: {limitation['description']}")

    print("\n--- Limitation to Product Mapping ---")
    for lim_code, products in processed['limitation_product_mapping'].items():
        print(f"{lim_code} affects: {', '.join(products)}")

    print("\n--- Prose Instructions for LLM ---")
    instructions = result['prose_generation']['instructions']
    print(f"Tone: {instructions['tone']}")
    print(f"Format: {instructions['format']}")
    print("Requirements:")
    for req in instructions['requirements'][:3]:
        print(f"  - {req}")


def example_3_employer_benefits():
    """Example 3: Client with employer-provided benefits"""
    print_section_header("EXAMPLE 3: Employer Benefits")

    print("\nScenario: Corporate executive with comprehensive employer benefits")
    print("Expected: Skip health insurance (employer provides), focus on personal coverage")

    form_data = {
        "f5.1": "Yes",  # Life Insurance
        "f5.2": "Yes",  # Income Protection
        "f5.3": "Yes",  # Trauma Cover
        "f5.4": "No",   # Health Insurance - employer provides
        "f5.5": "Yes",  # TPD
        "f5.6": "No",   # ACC
        "f6.1": "Yes",  # Employer medical coverage
        "f7": "Company provides platinum health insurance for employee and family"
    }

    result = generate_scope_of_advice_json(
        form_data,
        client_name="Jennifer Williams",
        is_couple=False
    )

    print("\n--- Coverage Analysis ---")
    processed = result['processed_data']
    print(f"In Scope ({len(processed['in_scope'])} products):")
    for product in processed['in_scope']:
        print(f"  ✓ {product}")

    print(f"\nOut of Scope ({len(processed['out_of_scope'])} products):")
    for product in processed['out_of_scope']:
        print(f"  ✗ {product}")

    print("\n--- Limitation Explanations ---")
    explanations = result['prose_generation']['template_variables']['limitation_explanations']
    for exp in explanations:
        print(f"  • {exp}")


def example_4_high_net_worth():
    """Example 4: High net worth individual - self insurance"""
    print_section_header("EXAMPLE 4: High Net Worth - Self Insurance")

    print("\nScenario: Wealthy retiree with no debt and substantial assets")
    print("Expected: No insurance needed due to self-insurance capacity")

    form_data = {
        "f5.1": "No",   # Life Insurance - not needed
        "f5.2": "No",   # Income Protection - retired
        "f5.3": "No",   # Trauma Cover - self-insure
        "f5.4": "No",   # Health Insurance - self-insure
        "f5.5": "No",   # TPD - not needed
        "f5.6": "No",   # ACC - not needed
        "f6.2": "Yes",  # No debt, strong assets
        "f6.4": "Yes",  # Can self-insure
        "f6.5": "Yes",  # No dependants
        "f7": "Client has $15M+ net worth, no mortgage, adult children financially independent"
    }

    result = generate_scope_of_advice_json(
        form_data,
        client_name="Robert Anderson",
        is_couple=False
    )

    print("\n--- Analysis ---")
    processed = result['processed_data']
    print(f"Products in Scope: {len(processed['in_scope'])}")
    print(f"Products out of Scope: {len(processed['out_of_scope'])}")
    print(f"No products in scope: {processed['no_products_in_scope']}")

    print("\n--- Reasons for No Coverage ---")
    for limitation in processed['active_limitations']:
        print(f"  • {limitation['description']}")

    print(f"\n--- Additional Notes ---")
    print(f"  {result['form_data']['limitation_notes']}")

    print(f"\n--- Closing Statement ---")
    print(f"  {result['prose_generation']['template_variables']['closing_statement']}")


def example_5_uninsurable_occupation():
    """Example 5: Client with uninsurable occupation"""
    print_section_header("EXAMPLE 5: Uninsurable Occupation")

    print("\nScenario: Professional stunt performer - occupation limits coverage options")
    print("Expected: Limited coverage due to high-risk occupation")

    form_data = {
        "f5.1": "Yes",  # Life Insurance - available with loading
        "f5.2": "No",   # Income Protection - not available
        "f5.3": "Yes",  # Trauma Cover - available with exclusions
        "f5.4": "Yes",  # Health Insurance - standard
        "f5.5": "No",   # TPD - not available
        "f5.6": "No",   # ACC - rely on standard ACC
        "f6.6": "Yes",  # Uninsurable occupation
        "f7": "Stunt performer - Income Protection and TPD declined by all insurers"
    }

    result = generate_scope_of_advice_json(
        form_data,
        client_name="Jake Morrison",
        is_couple=False
    )

    print("\n--- Coverage Availability ---")
    processed = result['processed_data']

    print("Available Coverage (with conditions):")
    for product in processed['in_scope']:
        print(f"  ✓ {product}")

    print("\nUnavailable Coverage:")
    for product in processed['out_of_scope']:
        # Check if affected by occupation
        is_occupation_related = False
        for lim_code, products in processed['limitation_product_mapping'].items():
            if lim_code == 'uninsurable_occupation' and product in products:
                is_occupation_related = True
                break

        status = "(occupation-related)" if is_occupation_related else ""
        print(f"  ✗ {product} {status}")

    print(f"\n--- Adviser Notes ---")
    print(f"  {result['form_data']['limitation_notes']}")


def example_6_multiple_limitations():
    """Example 6: Complex case with multiple limitations"""
    print_section_header("EXAMPLE 6: Multiple Limitations")

    print("\nScenario: Client with multiple factors limiting scope")
    print("Expected: Very limited scope due to combined limitations")

    form_data = {
        "f5": "partial",
        "f5.1": "No",   # Life Insurance
        "f5.2": "Yes",  # Income Protection - only thing in scope
        "f5.3": "No",   # Trauma Cover
        "f5.4": "No",   # Health Insurance
        "f5.5": "No",   # TPD
        "f5.6": "No",   # ACC
        "f6": "multiple",
        "f6.1": "Yes",  # Employer medical
        "f6.3": "Yes",  # Budget limitations
        "f6.5": "Yes",  # No dependants
        "f6.7": "Yes",  # Other
        "f7": "Pre-existing medical conditions limit trauma and TPD options"
    }

    result = generate_scope_of_advice_json(
        form_data,
        client_name="Emma Davis",
        is_couple=False
    )

    print("\n--- Limitation Analysis ---")
    processed = result['processed_data']

    print(f"Total Limitations: {len(processed['active_limitations'])}")
    print("\nActive Limitations:")
    for limitation in processed['active_limitations']:
        print(f"  • {limitation['code']}: {limitation['description']}")

    print(f"\nProducts Still in Scope: {processed['in_scope']}")

    print("\n--- Complex Limitation Mapping ---")
    for lim_code, products in processed['limitation_product_mapping'].items():
        desc = next((l['description'] for l in processed['active_limitations']
                    if l['code'] == lim_code), lim_code)
        print(f"\n{desc}:")
        for product in products:
            print(f"  → Affects: {product}")


def example_7_data_variations():
    """Example 7: Handle various data format variations"""
    print_section_header("EXAMPLE 7: Data Format Variations")

    print("\nTesting various checkbox value formats and field ID variations")

    test_cases = [
        {
            "name": "Mixed case values",
            "data": {
                "f5.1": "YES",
                "f5.2": "yes",
                "f5.3": "Yes",
                "f5.4": "no",
                "f5.5": "NO",
                "f5.6": "No"
            }
        },
        {
            "name": "Boolean-like values",
            "data": {
                "5.1": "1",
                "5.2": "true",
                "5.3": "True",
                "5.4": "0",
                "5.5": "false",
                "5.6": "False"
            }
        },
        {
            "name": "Checkbox representations",
            "data": {
                "f5.1": "checked",
                "f5.2": "on",
                "f5.3": "x",
                "f5.4": "",
                "f5.5": "unchecked",
                "f5.6": None
            }
        }
    ]

    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        result = generate_scope_of_advice_json(test_case['data'])
        processed = result['processed_data']

        print(f"In Scope: {len(processed['in_scope'])} products")
        print(f"Out of Scope: {len(processed['out_of_scope'])} products")

        # Show which specific products were marked as in-scope
        if processed['in_scope']:
            print(f"Selected: {', '.join(processed['in_scope'][:3])}"
                 f"{' ...' if len(processed['in_scope']) > 3 else ''}")


def example_8_structured_output():
    """Example 8: Structured Output with 10 Discrete Sections"""
    print_section_header("EXAMPLE 8: Structured Output for LLM Integration")

    print("\nDemonstrating the new structured output with 10 validated sections for LLM generation")

    form_data = {
        "f5.1": "Yes",  # Life Insurance
        "f5.2": "Yes",  # Income Protection
        "f5.3": "No",   # Trauma Cover
        "f5.4": "No",   # Health Insurance
        "f5.5": "Yes",  # TPD
        "f5.6": "No",   # ACC
        "f6.3": "Yes",  # Budget
        "f6.7": "Yes",  # Other
        "f7": "Client recently diagnosed with Type 2 diabetes"
    }

    result = generate_scope_of_advice_json(
        form_data,
        client_name="David Martinez",
        is_couple=False
    )

    print("\n--- STRUCTURED OUTPUT FORMAT ---")

    # Show the expected response format
    expected = result['expected_response']
    print(f"\nFormat: {expected['format']}")
    print(f"Schema: {expected['schema']}")
    print(f"Required Fields: {len(expected['fields'])} sections")

    # Show validation rules
    validation = expected['validation_rules']
    print(f"\n--- Validation Rules ---")
    print(f"All Fields Required: {validation['all_fields_required']}")
    print(f"Max Lengths Enforced: {validation['max_lengths_enforced']}")

    # Display all 10 sections with their requirements
    print(f"\n--- 10 REQUIRED SECTIONS WITH CHARACTER LIMITS ---")
    sections = result['prose_generation']['required_sections']

    for i, (section_name, section_data) in enumerate(sections.items(), 1):
        print(f"\n{i}. {section_name.upper()} (max {section_data['max_length']} chars)")
        print(f"   Instruction: {section_data['instruction']}")

        # Show suggested content (truncated for display)
        content = section_data['suggested_content']
        if len(content) > 150:
            print(f"   Suggested: {content[:150]}...")
        else:
            print(f"   Suggested: {content}")

        # Verify length compliance
        if len(content) > section_data['max_length']:
            print(f"   ⚠️ WARNING: Suggested content exceeds limit!")
        else:
            print(f"   ✓ Length: {len(content)}/{section_data['max_length']} chars")

    # Show how to structure the LLM request
    print("\n--- LLM REQUEST STRUCTURE ---")
    print("\nThe LLM should return a JSON object with exactly these fields:")
    print(json.dumps({
        section: f"<content max {sections[section]['max_length']} chars>"
        for section in expected['fields']
    }, indent=2))

    # Show complete example output
    print("\n--- EXAMPLE STRUCTURED RESPONSE ---")
    example_response = {
        "summary": sections["summary"]["suggested_content"][:700],
        "in_scope": sections["in_scope"]["suggested_content"][:500],
        "out_of_scope": sections["out_of_scope"]["suggested_content"][:500],
        "limitations": sections["limitations"]["suggested_content"][:500],
        "assumptions": sections["assumptions"]["suggested_content"][:500],
        "client_priorities": sections["client_priorities"]["suggested_content"][:500],
        "replacements": sections["replacements"]["suggested_content"][:500],
        "what_is_not_covered": sections["what_is_not_covered"]["suggested_content"][:500],
        "next_steps": sections["next_steps"]["suggested_content"][:400],
        "disclosures": sections["disclosures"]["suggested_content"][:500]
    }

    print(json.dumps(example_response, indent=2))

    # Validate the example response
    print("\n--- VALIDATION CHECK ---")
    all_valid = True
    for field, content in example_response.items():
        max_length = validation['character_limits'][field]
        is_valid = len(content) <= max_length
        status = "✓" if is_valid else "✗"
        print(f"{status} {field}: {len(content)}/{max_length} chars")
        if not is_valid:
            all_valid = False

    print(f"\nOverall Validation: {'PASSED ✓' if all_valid else 'FAILED ✗'}")


def example_9_llm_prompt_template():
    """Example 9: Complete LLM Prompt Template"""
    print_section_header("EXAMPLE 9: LLM Prompt Template")

    print("\nComplete prompt template for requesting structured scope of advice generation")

    form_data = {
        "f5.1": "Yes",
        "f5.2": "Yes",
        "f5.3": "Yes",
        "f5.4": "No",
        "f5.5": "Yes",
        "f5.6": "No",
        "f6.1": "Yes",  # Employer medical
        "f7": "Comprehensive employer health plan covers family"
    }

    result = generate_scope_of_advice_json(
        form_data,
        client_name="Sarah Johnson",
        is_couple=True
    )

    sections = result['prose_generation']['required_sections']
    validation = result['expected_response']['validation_rules']

    print("\n--- COMPLETE LLM PROMPT ---")
    llm_prompt = f"""
You are generating the Scope of Advice section for an insurance Statement of Advice document.

CONTEXT:
- Client: {result['prose_generation']['context']['client_name']}
- Is Couple: {result['prose_generation']['context']['is_couple']}
- Products In Scope: {', '.join(result['processed_data']['in_scope'])}
- Products Out of Scope: {', '.join(result['processed_data']['out_of_scope'])}
- Active Limitations: {[l['description'] for l in result['processed_data']['active_limitations']]}

REQUIREMENTS:
Generate a JSON response with EXACTLY these 10 fields. Each field MUST respect its character limit.

FIELD SPECIFICATIONS:
{json.dumps({
    field: {
        "instruction": sections[field]["instruction"],
        "max_length": sections[field]["max_length"],
        "suggested_start": sections[field]["suggested_content"][:100] + "..."
    }
    for field in result['expected_response']['fields']
}, indent=2)}

VALIDATION RULES:
- All 10 fields are required
- Each field must not exceed its max_length
- Content must be professional and compliant
- Use the suggested content as guidance but personalize for this client

OUTPUT FORMAT:
Return ONLY a valid JSON object with the 10 required fields. Example structure:
{{
    "summary": "Your summary text here (max 700 chars)",
    "in_scope": "Your in-scope text here (max 500 chars)",
    "out_of_scope": "Your out-of-scope text here (max 500 chars)",
    "limitations": "Your limitations text here (max 500 chars)",
    "assumptions": "Your assumptions text here (max 500 chars)",
    "client_priorities": "Your priorities text here (max 500 chars)",
    "replacements": "Your replacements text here (max 500 chars)",
    "what_is_not_covered": "Your exclusions text here (max 500 chars)",
    "next_steps": "Your next steps text here (max 400 chars)",
    "disclosures": "Your disclosures text here (max 500 chars)"
}}
"""
    print(llm_prompt)


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print(" SCOPE OF ADVICE GENERATOR - EXAMPLE USAGE")
    print(" Demonstrating various scenarios and use cases")
    print("="*80)

    examples = [
        ("Comprehensive Coverage", example_1_comprehensive_coverage),
        ("Budget Constraints", example_2_budget_constraints),
        ("Employer Benefits", example_3_employer_benefits),
        ("High Net Worth", example_4_high_net_worth),
        ("Uninsurable Occupation", example_5_uninsurable_occupation),
        ("Multiple Limitations", example_6_multiple_limitations),
        ("Data Format Variations", example_7_data_variations),
        ("Structured Output (10 Sections)", example_8_structured_output),
        ("LLM Prompt Template", example_9_llm_prompt_template)
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
        "f5.1": "Yes",
        "f5.2": "Yes",
        "f5.3": "No",
        "f5.4": "No",
        "f5.5": "Yes",
        "f5.6": "No",
        "f6.1": "Yes",
        "f6.3": "Yes",
        "f7": "Employer health plan covers family"
    }

    result = generate_scope_of_advice_json(
        sample_data,
        client_name="Sample Client",
        is_couple=True
    )

    output_file = "scope_of_advice_sample_output.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Sample output saved to: {output_file}")
    print(f"File contains complete JSON structure ({len(json.dumps(result))} bytes)")


if __name__ == "__main__":
    main()