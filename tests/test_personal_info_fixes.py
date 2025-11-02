"""
Quick test to verify personal information extractor fixes
"""

import sys
sys.path.insert(0, 'src')

from processors.personal_information_extractor import extract_personal_information
import json

print("=" * 70)
print("TESTING PERSONAL INFORMATION EXTRACTOR FIXES")
print("=" * 70)

# Test 1: Single person with edge cases
print("\n1. Single Person Test (edge cases)")
print("-" * 70)

single_test = {
    "144": "John",  # First name (not falling back to email)
    "145": "Smith",  # Last name
    "3": "john@example.com",  # Email (should NOT be used as name)
    "94": "2025-10-30 01:13:38",  # DOB with timestamp format
    "6": "Software Engineer",  # Occupation
    "276": "no",  # Not self-employed
    "277": "",  # Employer blank (should stay blank, not "Self-Employed")
    "10": "75000",  # Salary
    "275": "35+ hours",  # Hours with + sign
    "26": "yes"  # Will status
}

result1 = extract_personal_information(single_test)
print(json.dumps(result1, indent=2))

assert result1["status"] == "success", "Should have status field"
assert result1["household"]["people"][0]["label"] == "John", "Name should be John not email"
assert result1["household"]["people"][0]["employer"] == "", "Employer should be blank not Self-Employed"
assert result1["household"]["people"][0]["employment_status"] == "Fulltime", "35+ hours should be Fulltime"
assert result1["household"]["people"][0]["age"] > 0, "Timestamp DOB should parse to age"
print("✅ All single person tests passed!")

# Test 2: Couple with self-employed
print("\n2. Couple Test (with self-employed)")
print("-" * 70)

couple_test = {
    "144": "Jane",
    "145": "Doe",
    "94": "1985-03-15",
    "6": "Consultant",
    "276": "yes",  # Self-employed
    "277": "Some Company",  # Should be overridden to "Self-Employed"
    "10": "100000",
    "275": "40",
    "26": "yes",
    "146": "Mike",  # Partner first name
    "147": "Doe",  # Partner last name
    "39": "Couple",  # Case variant of "couple"
    "95": "1983-07-22",
    "40": "Designer",
    "483": "no",  # Partner not self-employed
    "288": "Design Studio",  # Partner employer
    "296": "85000",
    "295": "20 hrs",  # Part-time hours
    "300": "no"
}

result2 = extract_personal_information(couple_test)
print(json.dumps(result2, indent=2))

assert len(result2["household"]["people"]) == 2, "Should have 2 people"
assert result2["household"]["people"][0]["employer"] == "Self-Employed", "Main should be self-employed"
assert result2["household"]["people"][0]["employment_status"] == "Self-Employed", "Status should be Self-Employed"
assert result2["household"]["people"][1]["employer"] == "Design Studio", "Partner employer should be preserved"
assert result2["household"]["people"][1]["employment_status"] == "Part-time", "20 hrs should be Part-time"
print("✅ All couple tests passed!")

# Test 3: Negative salary and zero hours
print("\n3. Edge Case Test (negative salary, zero hours)")
print("-" * 70)

edge_test = {
    "144": "Test",
    "145": "User",
    "94": "1990-01-01",
    "6": "Tester",
    "276": "false",
    "277": "Test Corp",
    "10": "-5000",  # Negative salary should clamp to 0
    "275": "0",  # Zero hours
    "26": ""
}

result3 = extract_personal_information(edge_test)
print(json.dumps(result3, indent=2))

assert result3["household"]["people"][0]["salary_before_tax_nzd"] == 0, "Negative salary should clamp to 0"
assert result3["household"]["people"][0]["employment_status"] == "Fulltime", "Zero hours defaults to Fulltime"
print("✅ All edge case tests passed!")

print("\n" + "=" * 70)
print("🎉 ALL TESTS PASSED - PERSONAL INFO EXTRACTOR IS MVP-READY!")
print("=" * 70)
