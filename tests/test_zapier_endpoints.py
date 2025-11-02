#!/usr/bin/env python3
"""
Test Script for Zapier-Compatible Endpoints

This script tests the new generator endpoints that Zapier will use
to process insurance form data and generate structured content.

Created: 2025-01-27
Author: Insurance SOA System
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime


BASE_URL = "http://localhost:5001"


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def test_scope_of_advice_endpoint():
    """Test the Scope of Advice endpoint"""
    print_header("Testing Scope of Advice Endpoint")

    # Test data matching automation form
    test_data = {
        "client_name": "John Smith",
        "is_couple": False,
        "f5.1": "Yes",  # Life Insurance
        "f5.2": "Yes",  # Income Protection
        "f5.3": "No",   # Trauma
        "f5.4": "No",   # Health
        "f5.5": "Yes",  # TPD
        "f5.6": "No",   # ACC
        "f6.1": "Yes",  # Employer medical limitation
        "f6.3": "Yes",  # Budget limitation
        "f7": "Budget constraints limit coverage options"
    }

    try:
        req = urllib.request.Request(
            f"{BASE_URL}/generate/scope-of-advice",
            data=json.dumps(test_data).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )

        response = urllib.request.urlopen(req)

        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            print("✅ SUCCESS - Status Code: 200")
            print(f"Client: {data['client_name']}")
            print(f"Products in scope: {', '.join(data['products_in_scope'])}")
            print(f"Products out of scope: {', '.join(data['products_out_of_scope'])}")
            print(f"Has limitations: {data['has_limitations']}")
            print(f"Sections generated: {len(data['sections'])}")
            print(f"All sections valid: {data['validation']['all_sections_present']}")

            # Show first section
            first_section = list(data['sections'].keys())[0]
            print(f"\nSample content ({first_section}):")
            print(f"  {data['sections'][first_section][:150]}...")

            return True
        else:
            print(f"❌ FAILED - Status Code: {response.status}")
            return False

    except urllib.error.URLError as e:
        print("❌ CONNECTION ERROR - Is the server running?")
        print("Start the server with: python3 src/webhook_server.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_where_are_you_now_endpoint():
    """Test the Where Are You Now endpoint"""
    print_header("Testing Where Are You Now Endpoint")

    # Test data matching fact find
    test_data = {
        "client_name": "Sarah Johnson",
        "is_couple": True,
        "f144": "Sarah",
        "f146": "Mike",
        "f95": "1985-06-15",
        "f6": "Engineer",
        "f40": "Teacher",
        "f10": "115000",
        "f42": "75000",
        "f16": "750000",  # House value
        "f15": "420000",  # Mortgage
        "f61": "85000",   # KiwiSaver
        "f215": "62000",  # Partner KiwiSaver
        "f33": "Savings",
        "f26": "35000",
        "f71": "Credit Card",
        "f72": "8000",
        "f501": "Yes"     # Will in place
    }

    try:
        req = urllib.request.Request(
            f"{BASE_URL}/generate/where-are-you-now",
            data=json.dumps(test_data).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )

        response = urllib.request.urlopen(req)

        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            print("✅ SUCCESS - Status Code: 200")
            print(f"Client: {data['client_name']}")
            print(f"Is Couple: {data['is_couple']}")

            # Show financial summary
            summary = data['financial_summary']
            print(f"\nFinancial Summary:")
            print(f"  Net Worth: ${summary['net_worth']:,.0f}")
            print(f"  Total Assets: ${summary['total_assets']:,.0f}")
            print(f"  Total Liabilities: ${summary['total_liabilities']:,.0f}")
            print(f"  Annual Income: ${summary['total_income']:,.0f}")

            print(f"\nSections generated: {len(data['sections'])}")
            print(f"All sections valid: {data['validation']['all_sections_present']}")

            # Show first section
            first_section = list(data['sections'].keys())[0]
            print(f"\nSample content ({first_section}):")
            print(f"  {data['sections'][first_section][:150]}...")

            return True
        else:
            print(f"❌ FAILED - Status Code: {response.status}")
            return False

    except urllib.error.URLError as e:
        print("❌ CONNECTION ERROR - Is the server running?")
        print("Start the server with: python3 src/webhook_server.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_combined_report_endpoint():
    """Test the Combined Report endpoint"""
    print_header("Testing Combined Report Endpoint")

    # Combined test data
    test_data = {
        "client_name": "Michael and Emma Brown",
        "is_couple": True,

        # Fact find data (for Where Are You Now)
        "f144": "Michael",
        "f146": "Emma",
        "f95": "1982-03-20",
        "f6": "Business Owner",
        "f40": "Consultant",
        "f10": "180000",
        "f42": "120000",
        "f16": "1200000",
        "f15": "650000",
        "f61": "125000",

        # Automation data (for Scope of Advice)
        "f5.1": "Yes",
        "f5.2": "Yes",
        "f5.3": "Yes",
        "f5.4": "No",
        "f5.5": "Yes",
        "f6.1": "Yes",

        "f501": "Yes"
    }

    try:
        req = urllib.request.Request(
            f"{BASE_URL}/generate/combined-report",
            data=json.dumps(test_data).encode('utf-8'),
            headers={"Content-Type": "application/json"}
        )

        response = urllib.request.urlopen(req)

        if response.status == 200:
            data = json.loads(response.read().decode('utf-8'))
            print("✅ SUCCESS - Status Code: 200")
            print(f"Client: {data['client_name']}")
            print(f"Is Couple: {data['is_couple']}")

            # Scope of Advice summary
            scope = data['scope_of_advice']
            print(f"\n📋 Scope of Advice:")
            print(f"  In Scope: {', '.join(scope['products_in_scope'][:3])}...")
            print(f"  Sections: {len(scope['sections'])}")

            # Where Are You Now summary
            where = data['where_are_you_now']
            print(f"\n💰 Where Are You Now:")
            print(f"  Net Worth: ${where['financial_summary']['net_worth']:,.0f}")
            print(f"  Total Income: ${where['financial_summary']['total_income']:,.0f}")
            print(f"  Sections: {len(where['sections'])}")

            print(f"\n✅ Total sections generated: {data['validation']['total_sections_generated']}")
            print(f"✅ All sections valid: {data['validation']['all_sections_valid']}")

            return True
        else:
            print(f"❌ FAILED - Status Code: {response.status}")
            return False

    except urllib.error.URLError as e:
        print("❌ CONNECTION ERROR - Is the server running?")
        print("Start the server with: python3 src/webhook_server.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_health_check():
    """Test if server is running"""
    print_header("Health Check")

    try:
        response = urllib.request.urlopen(f"{BASE_URL}/health")

        if response.status == 200:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"⚠️ Server responded with status: {response.status}")
            return False

    except urllib.error.URLError as e:
        print("❌ Cannot connect to server")
        print("Please start the server with: python3 src/webhook_server.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def create_zapier_webhook_example():
    """Create example Zapier webhook configuration"""
    print_header("Zapier Webhook Configuration")

    print("\n📌 ZAPIER WEBHOOK SETUP:")
    print("\n1. In Zapier, create a new Zap")
    print("2. Choose 'Webhooks by Zapier' as the trigger")
    print("3. Select 'Custom Request' as the event")
    print("\n4. Configure the webhook:")

    webhook_config = {
        "url": f"{BASE_URL}/generate/combined-report",
        "method": "POST",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": {
            "client_name": "{{client_name}}",
            "is_couple": "{{is_couple}}",
            "f144": "{{main_first_name}}",
            "f95": "{{date_of_birth}}",
            "f6": "{{occupation}}",
            "f10": "{{annual_income}}",
            "f16": "{{house_value}}",
            "f15": "{{mortgage}}",
            "f5.1": "{{life_insurance}}",
            "f5.2": "{{income_protection}}",
            # ... map other fields from your form
        }
    }

    print(f"\nURL: {webhook_config['url']}")
    print(f"Method: {webhook_config['method']}")
    print(f"Headers: {json.dumps(webhook_config['headers'], indent=2)}")
    print("\nBody (map these fields from your Gravity Forms data):")
    print(json.dumps(webhook_config['body'], indent=2))

    print("\n5. In the action step, process the response:")
    print("   - The response will contain 20 pre-generated sections")
    print("   - Pass these sections to your LLM (GPT, Claude, etc.)")
    print("   - Or use them directly in your document generation")


def main():
    """Run all endpoint tests"""
    print("\n" + "🧪"*30)
    print(" ZAPIER ENDPOINT TESTING")
    print(" Testing Insurance SOA Generator Endpoints")
    print("🧪"*30)

    # Check server health first
    if not test_health_check():
        print("\n⚠️ Server is not running!")
        print("Start the server first with:")
        print("  cd /Users/mitchworthington/Downloads/Insurance-SOA-main")
        print("  python3 src/webhook_server.py")
        return False

    # Test all endpoints
    results = []
    results.append(("Scope of Advice", test_scope_of_advice_endpoint()))
    results.append(("Where Are You Now", test_where_are_you_now_endpoint()))
    results.append(("Combined Report", test_combined_report_endpoint()))

    # Show Zapier configuration
    create_zapier_webhook_example()

    # Summary
    print_header("TEST SUMMARY")
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n" + "🎉"*30)
        print(" ALL TESTS PASSED!")
        print(" Endpoints are ready for Zapier integration")
        print("🎉"*30)
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)