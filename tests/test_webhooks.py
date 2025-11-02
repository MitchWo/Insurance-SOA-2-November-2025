#!/usr/bin/env python3
"""
Test script to simulate webhook calls to the Insurance SOA server
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:5001"


def print_section(title):
    """Print a formatted section header"""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)
    print()


def print_response(response):
    """Pretty print JSON response"""
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)
    print()


def test_health_check():
    """Test the health endpoint"""
    print_section("TEST 1: Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print_response(response)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Could not connect to server. Is it running?")
        print("  Start the server with: python src/webhook_server.py")
        return False


def test_initial_status():
    """Get initial system status"""
    print_section("TEST 2: Initial System Status")

    response = requests.get(f"{BASE_URL}/status")
    print(f"Status Code: {response.status_code}")
    print_response(response)


def test_fact_find_submission():
    """Test submitting a fact find form"""
    print_section("TEST 3: Submit Fact Find Form")

    # Load test data
    test_file = Path("data/test_webhook_fact_find.json")
    with open(test_file, 'r') as f:
        data = json.load(f)

    print("Submitting fact find for: sarah.johnson@example.com")
    print(f"Case ID: {data.get('f516')}")
    print()

    response = requests.post(
        f"{BASE_URL}/webhook/fact-find",
        json=data,
        headers={'Content-Type': 'application/json'}
    )

    print(f"Status Code: {response.status_code}")
    print_response(response)

    return response.status_code == 200


def test_automation_form_submission():
    """Test submitting an automation form"""
    print_section("TEST 4: Submit Automation Form")

    # Load test data
    test_file = Path("data/test_webhook_automation.json")
    with open(test_file, 'r') as f:
        data = json.load(f)

    print("Submitting automation form for: sarah.johnson@example.com")
    print(f"Provider: {data.get('f41')}")
    print()

    response = requests.post(
        f"{BASE_URL}/webhook/automation-form",
        json=data,
        headers={'Content-Type': 'application/json'}
    )

    print(f"Status Code: {response.status_code}")
    print_response(response)

    return response.status_code == 200


def test_final_status():
    """Get final system status"""
    print_section("TEST 5: Final System Status")

    response = requests.get(f"{BASE_URL}/status")
    print(f"Status Code: {response.status_code}")
    print_response(response)


def test_matches():
    """Get all matches"""
    print_section("TEST 6: View All Matches")

    response = requests.get(f"{BASE_URL}/matches")
    print(f"Status Code: {response.status_code}")
    print_response(response)


def test_unmatched_submission():
    """Test submitting a form that won't match"""
    print_section("TEST 7: Submit Unmatched Form")

    # Create data with different email
    data = {
        "f516": "CASE-2024-UNMATCHED",
        "f219": "unmatched@example.com",
        "f8": "single",
        "f144": "John",
        "f145": "Unmatched",
        "f94": "1990-01-01",
        "f6": "Developer",
        "f10": "100000"
    }

    print("Submitting fact find for: unmatched@example.com")
    print("(This should NOT match any automation form)")
    print()

    response = requests.post(
        f"{BASE_URL}/webhook/fact-find",
        json=data,
        headers={'Content-Type': 'application/json'}
    )

    print(f"Status Code: {response.status_code}")
    print_response(response)


def run_all_tests():
    """Run all webhook tests"""
    print("=" * 70)
    print("WEBHOOK TESTING SUITE")
    print("=" * 70)
    print()
    print("This script will test the webhook endpoints by submitting forms")
    print("and checking the responses.")
    print()

    # Test 1: Health check
    if not test_health_check():
        print()
        print("Cannot proceed without server running. Exiting.")
        return False

    # Test 2: Initial status
    test_initial_status()

    time.sleep(1)

    # Test 3: Submit fact find
    if not test_fact_find_submission():
        print("✗ Fact find submission failed")
        return False

    time.sleep(1)

    # Test 4: Submit automation form (should match with fact find)
    if not test_automation_form_submission():
        print("✗ Automation form submission failed")
        return False

    time.sleep(1)

    # Test 5: Check status
    test_final_status()

    time.sleep(1)

    # Test 6: View matches
    test_matches()

    time.sleep(1)

    # Test 7: Submit unmatched form
    test_unmatched_submission()

    # Final summary
    print_section("TEST SUMMARY")
    print("✓ All tests completed!")
    print()
    print("Check the following directories:")
    print("  - data/forms/fact_finds/      (saved fact find forms)")
    print("  - data/forms/automation_forms/ (saved automation forms)")
    print("  - data/reports/                (generated reports)")
    print()

    return True


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Error running tests: {e}")
