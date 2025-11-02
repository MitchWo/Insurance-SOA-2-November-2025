#!/usr/bin/env python3
"""Test trauma insurance fields extraction"""

import json
from src.generators.trauma_insurance_fields import extract_trauma_insurance_fields

# Load test data from the file
with open('test_with_trauma.json', 'r') as f:
    test_data = json.load(f)

# Extract trauma insurance fields
result = extract_trauma_insurance_fields(test_data)

# Pretty print the result
print('Extracted Trauma Insurance Fields:')
print('=' * 50)
print(json.dumps(result, indent=2))

# Verify calculations
print('\nVerification:')
print('-' * 50)
print(f'Main Contact Trauma Needs:')
print(f'  Replacement Income: ${result["main_replacement_income"]:,.0f}')
print(f'  Replacement Expenses: ${result["main_replacement_expenses"]:,.0f}')
print(f'  Debt Repayment: ${result["main_debt_repayment"]:,.0f}')
print(f'  Medical Bills: ${result["main_medical_bills"]:,.0f}')
print(f'  Childcare Assistance: ${result["main_childcare_assistance"]:,.0f}')
print(f'  Total Trauma Coverage: ${result["main_total_trauma"]:,.0f}')
print(f'  Needs Trauma Insurance: {result["main_needs_trauma"]}')
print(f'  Coverage Level: {result["trauma_coverage_level"]}')
print(f'  Recommendation Status: {result["trauma_recommendation_status"]}')