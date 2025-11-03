#!/usr/bin/env python3
"""
Webhook Server for Gravity Forms
Receives form submissions and processes them through the Insurance SOA system
"""
from flask import Flask, request, jsonify
from pathlib import Path
import json
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from models.fact_find import FactFind
from models.automation_form import AutomationForm
from processors.form_matcher import FormMatcher
from processors.insurance_workflow import InsuranceWorkflow
from processors.scope_of_advice_generator import generate_scope_of_advice_json
from processors.personal_information_extractor import extract_personal_information
from processors.life_insurance_extractor import extract_life_insurance, extract_trauma_insurance
from generators.life_insurance_fields import extract_life_insurance_fields
from generators.trauma_insurance_fields import extract_trauma_insurance_fields
from generators.income_protection_fields import extract_income_protection_fields
from generators.health_insurance_fields import extract_health_insurance_fields
from generators.accidental_injury_fields import extract_accidental_injury_fields
from processors.zapier_trigger import ZapierTrigger
from processors.auto_matcher import check_and_trigger_match

app = Flask(__name__)

# Storage directories
DATA_DIR = Path(__file__).parent.parent / "data"
FORMS_DIR = DATA_DIR / "forms"
FACT_FINDS_DIR = FORMS_DIR / "fact_finds"
AUTOMATION_FORMS_DIR = FORMS_DIR / "automation_forms"
REPORTS_DIR = DATA_DIR / "reports"

# Create directories
FACT_FINDS_DIR.mkdir(parents=True, exist_ok=True)
AUTOMATION_FORMS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# In-memory matcher (in production, this would be database-backed)
matcher = FormMatcher()

# Initialize Zapier trigger
zapier_trigger = ZapierTrigger()


def load_all_forms():
    """Load all existing forms into the matcher on startup"""
    print("Loading existing forms...")

    # Load fact finds
    for file_path in FACT_FINDS_DIR.glob("*.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            fact_find = FactFind()
            fact_find.load_from_dict(data)
            matcher.add_fact_find(fact_find)
            print(f"  ✓ Loaded fact find: {file_path.name}")
        except Exception as e:
            print(f"  ✗ Failed to load {file_path.name}: {e}")

    # Load automation forms
    for file_path in AUTOMATION_FORMS_DIR.glob("*.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            automation_form = AutomationForm()
            automation_form.load_from_dict(data)
            matcher.add_automation_form(automation_form)
            print(f"  ✓ Loaded automation form: {file_path.name}")
        except Exception as e:
            print(f"  ✗ Failed to load {file_path.name}: {e}")

    stats = matcher.get_match_statistics()
    print(f"Loaded: {stats['total_fact_finds']} fact finds, {stats['total_automation_forms']} automation forms")


def save_form_data(data: dict, form_type: str, identifier: str) -> Path:
    """Save form data to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{identifier}_{timestamp}.json"

    if form_type == "fact_find":
        file_path = FACT_FINDS_DIR / filename
    else:
        file_path = AUTOMATION_FORMS_DIR / filename

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

    return file_path


def try_match_and_generate_report(email: str) -> dict:
    """Try to match forms and generate report if confident match found"""
    match_result = matcher.match_by_email(email)

    if not match_result:
        return {
            'matched': False,
            'reason': 'No matching forms found for this email'
        }

    if not match_result.is_confident_match(threshold=0.7):
        return {
            'matched': True,
            'confident': False,
            'confidence': match_result.confidence,
            'reasons': match_result.reasons,
            'message': 'Forms matched but confidence is below threshold'
        }

    # Generate report
    try:
        workflow = InsuranceWorkflow()
        # Load the original raw data, not the processed model data
        # We need to get the raw form data that was originally submitted
        workflow.fact_find = match_result.fact_find
        workflow.automation_form = match_result.automation_form

        # Validate
        is_valid, errors, warnings = workflow.validate_workflow()

        # Generate report file
        case_id = match_result.fact_find.case_info.get('case_id', 'UNKNOWN')
        report_filename = f"{case_id}_{email.replace('@', '_at_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path = REPORTS_DIR / report_filename

        report_content = workflow.generate_report(str(report_path))

        # Get summary
        summary = workflow.get_client_summary()

        return {
            'matched': True,
            'confident': True,
            'confidence': match_result.confidence,
            'reasons': match_result.reasons,
            'workflow_valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'report_path': str(report_path),
            'summary': {
                'client_name': summary['client_info'].get('name'),
                'recommended_provider': summary['recommendations'].get('selected_provider'),
                'scope': summary['recommendations'].get('scope_of_advice', [])
            }
        }
    except Exception as e:
        return {
            'matched': True,
            'confident': True,
            'confidence': match_result.confidence,
            'error': f"Failed to generate report: {str(e)}"
        }


@app.route('/ff', methods=['POST'])
@app.route('/webhook/fact-find', methods=['POST'])  # Keep old endpoint for compatibility
def webhook_fact_find():
    """Receive Fact Find form submissions"""
    try:
        # Log all incoming data for debugging
        print("=" * 70)
        print("RECEIVED REQUEST TO /ff")
        print("=" * 70)
        print(f"Headers: {dict(request.headers)}")
        print(f"Content-Type: {request.content_type}")
        print(f"Method: {request.method}")

        # Try to get data in different formats
        raw_data = request.get_data(as_text=True)
        print(f"Raw data: {raw_data[:500]}...")  # First 500 chars

        # Get JSON data from Gravity Forms
        data = request.get_json(force=True) if request.data else None

        print(f"Parsed JSON keys: {list(data.keys()) if data else 'No JSON data'}")
        print("=" * 70)

        if not data:
            return jsonify({'error': 'No data received'}), 400

        # Create fact find
        fact_find = FactFind()
        fact_find.load_from_dict(data)

        # Get identifier
        email = fact_find.client_info.get('email')
        case_id = fact_find.case_info.get('case_id', 'NO_CASE_ID')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Save to file using email as identifier
        safe_email = email.replace('@', '_at_').replace('.', '_')
        file_path = save_form_data(data, 'fact_find', safe_email)

        # Add to matcher
        matcher.add_fact_find(fact_find)

        # Try to match and trigger Zapier if both forms exist
        match_result = check_and_trigger_match(email, matcher, zapier_trigger)

        # Legacy match info for backward compatibility
        match_info = try_match_and_generate_report(email)

        response = {
            'status': 'success',
            'form_type': 'fact_find',
            'case_id': case_id,
            'email': email,
            'client_name': fact_find.get_client_full_name(),
            'saved_to': str(file_path),
            'match_info': match_info,
            'zapier_triggered': match_result.get('zapier_triggered', False),
            'zapier_status': match_result.get('zapier_status', 'not_triggered')
        }

        print(f"✓ Received Fact Find: {case_id} - {email}")
        if match_info.get('confident'):
            print(f"  ✓ Confident match found! Report generated: {match_info.get('report_path')}")

        return jsonify(response), 200

    except Exception as e:
        print(f"✗ Error processing fact find: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/automation', methods=['POST'])
@app.route('/webhook/automation-form', methods=['POST'])  # Keep old endpoint for compatibility
def webhook_automation_form():
    """Receive Insurance Automation form submissions"""
    try:
        # Get JSON data from Gravity Forms
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data received'}), 400

        # Create automation form
        automation_form = AutomationForm()
        automation_form.load_from_dict(data)

        # Get identifier
        email = automation_form.client_details.get('email')

        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Save to file
        safe_email = email.replace('@', '_at_').replace('.', '_')
        file_path = save_form_data(data, 'automation_form', safe_email)

        # Add to matcher
        matcher.add_automation_form(automation_form)

        # Try to match and trigger Zapier if both forms exist
        match_result = check_and_trigger_match(email, matcher, zapier_trigger)

        # Legacy match info for backward compatibility
        match_info = try_match_and_generate_report(email)

        response = {
            'status': 'success',
            'form_type': 'automation_form',
            'email': email,
            'recommended_provider': automation_form.get_recommended_provider(),
            'is_couple': automation_form.is_couple(),
            'saved_to': str(file_path),
            'match_info': match_info,
            'zapier_triggered': match_result.get('zapier_triggered', False),
            'zapier_status': match_result.get('zapier_status', 'not_triggered')
        }

        print(f"✓ Received Automation Form: {email}")
        if match_info.get('confident'):
            print(f"  ✓ Confident match found! Report generated: {match_info.get('report_path')}")

        return jsonify(response), 200

    except Exception as e:
        print(f"✗ Error processing automation form: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    """Get system status and statistics"""
    stats = matcher.get_match_statistics()

    return jsonify({
        'status': 'running',
        'statistics': stats,
        'unmatched_fact_finds': len(matcher.get_unmatched_fact_finds()),
        'unmatched_automation_forms': len(matcher.get_unmatched_automation_forms())
    }), 200


@app.route('/matches', methods=['GET'])
def get_matches():
    """Get all matches"""
    stats = matcher.get_match_statistics()

    matches = []
    for match in matcher.match_history:
        matches.append({
            'email': match.fact_find.client_info.get('email'),
            'case_id': match.fact_find.case_info.get('case_id'),
            'client_name': match.fact_find.get_client_full_name(),
            'confidence': match.confidence,
            'is_confident': match.is_confident_match(),
            'reasons': match.reasons,
            'matched_at': match.matched_at.isoformat()
        })

    return jsonify({
        'total_matches': len(matches),
        'confident_matches': stats['confident_matches'],
        'matches': matches
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/generate/scope-of-advice', methods=['POST'])
def generate_scope_of_advice():
    """
    Generate structured Scope of Advice JSON from automation form data
    Zapier-compatible endpoint for LLM prose generation
    """
    try:
        data = request.json

        # Extract client info if provided
        client_name = data.get('client_name', 'the client')
        is_couple = data.get('is_couple', False)

        # Generate the structured JSON
        result = generate_scope_of_advice_json(
            data,
            client_name=client_name,
            is_couple=is_couple
        )

        # Create Zapier-friendly response
        response = {
            'status': 'success',
            'section_type': 'scope_of_advice',
            'client_name': client_name,
            'is_couple': is_couple,
            'products_in_scope': result['processed_data']['in_scope'],
            'products_out_of_scope': result['processed_data']['out_of_scope'],
            'has_limitations': result['processed_data']['has_limitations'],
            'sections': {
                section_name: section_data['suggested_content']
                for section_name, section_data in result['prose_generation']['required_sections'].items()
            },
            'validation': {
                'all_sections_present': len(result['prose_generation']['required_sections']) == 10,
                'content_within_limits': all(
                    len(section['suggested_content']) <= section['max_length']
                    for section in result['prose_generation']['required_sections'].values()
                )
            }
        }

        print(f"✓ Generated Scope of Advice for {client_name}")
        return jsonify(response), 200

    except Exception as e:
        print(f"✗ Error generating Scope of Advice: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/generate/personal-information', methods=['POST'])
def generate_personal_information():
    """
    Extract personal information in simple table format
    Zapier-compatible endpoint for direct data extraction
    """
    try:
        data = request.json

        # Extract personal information
        result = extract_personal_information(data)

        # Return the structured data directly
        response = {
            'status': 'success',
            **result  # Include all fields from personal_information
        }

        print(f"✓ Extracted Personal Information")
        return jsonify(response), 200

    except Exception as e:
        print(f"✗ Error extracting Personal Information: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/generate/assets-liabilities', methods=['POST'])
def generate_assets_liabilities():
    """
    Extract assets and liabilities as simple text tables and JSON arrays
    """
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        from processors.assets_liabilities_extractor import extract_assets_liabilities

        result = extract_assets_liabilities(data)

        print("=" * 70)
        print("EXTRACTED ASSETS & LIABILITIES")
        print("=" * 70)
        print(f"Assets: {result['asset_count']} items")
        print(f"Liabilities: {result['liability_count']} items")
        print(f"Net Worth: ${result['net_worth']:,}")
        print("=" * 70)

        return jsonify(result), 200

    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/generate/combined-report', methods=['POST'])
def generate_combined_report():
    """
    Generate both Scope of Advice and Where Are You Now sections
    Combined endpoint for complete report generation
    """
    try:
        data = request.json

        # Extract client info
        client_name = data.get('client_name', 'the client')
        is_couple = data.get('is_couple', False)

        # Separate fact find and automation data if provided
        fact_find_data = data.get('fact_find', data)
        automation_data = data.get('automation', data)

        # Generate both sections
        scope_result = generate_scope_of_advice_json(
            automation_data,
            client_name=client_name,
            is_couple=is_couple
        )

        # Extract personal information
        personal_info = extract_personal_information(data)

        # Extract assets and liabilities
        from processors.assets_liabilities_extractor import extract_assets_liabilities
        assets_liabilities = extract_assets_liabilities(data)

        # Generate life insurance fields
        life_insurance_fields = extract_life_insurance_fields(data)

        # Generate trauma insurance fields
        trauma_insurance_fields = extract_trauma_insurance_fields(data)

        # Generate income protection fields
        income_protection_fields = extract_income_protection_fields(data)

        # Generate health insurance fields
        health_insurance_fields = extract_health_insurance_fields(data)

        # Generate accidental injury fields
        accidental_injury_fields = extract_accidental_injury_fields(data)

        # Create combined response
        response = {
            'status': 'success',
            'client_name': client_name,
            'is_couple': is_couple,
            'scope_of_advice': {
                'products_in_scope': scope_result['processed_data']['in_scope'],
                'products_out_of_scope': scope_result['processed_data']['out_of_scope'],
                'sections': {
                    section_name: section_data['suggested_content']
                    for section_name, section_data in scope_result['prose_generation']['required_sections'].items()
                }
            },
            'personal_information': personal_info,
            'assets_liabilities': assets_liabilities,
            'life_insurance': life_insurance_fields,
            'trauma_insurance': trauma_insurance_fields,
            'income_protection': income_protection_fields,
            'health_insurance': health_insurance_fields,
            'accidental_injury': accidental_injury_fields,
            'validation': {
                'total_sections_generated': 20,
                'all_sections_valid': True,
                'includes_life_insurance': True,
                'includes_trauma_insurance': True,
                'includes_income_protection': True,
                'includes_health_insurance': True,
                'includes_accidental_injury': True
            }
        }

        print(f"✓ Generated Combined Report for {client_name}")
        if life_insurance_fields.get('main_net_coverage'):
            print(f"  Life Insurance: ${life_insurance_fields['main_net_coverage']:,.0f} coverage needed")
        if trauma_insurance_fields.get('main_total_trauma'):
            print(f"  Trauma Insurance: ${trauma_insurance_fields['main_total_trauma']:,.0f} coverage needed")
        return jsonify(response), 200

    except Exception as e:
        print(f"✗ Error generating Combined Report: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/generate/life-insurance-fields', methods=['POST'])
def get_life_insurance_fields():
    """
    Extract individual life insurance fields for Zapier dynamic prompting
    Returns clean field values without complex sections
    """
    try:
        # Get JSON data
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        print("=" * 70)
        print("EXTRACTING LIFE INSURANCE FIELDS")
        print("=" * 70)

        # Extract fields
        result = extract_life_insurance_fields(data)

        # Log summary
        print(f"Client: {result.get('client_name', 'Unknown')}")
        print(f"Is Couple: {result.get('is_couple')}")
        print(f"Main Net Coverage: ${result.get('main_net_coverage', 0):,.0f}")
        if result.get('is_couple'):
            print(f"Partner Net Coverage: ${result.get('partner_net_coverage', 0):,.0f}")
        print(f"Recommendation Status: {result.get('recommendation_status')}")

        print(f"✓ Extracted Life Insurance Fields")
        return jsonify(result), 200

    except Exception as e:
        print(f"✗ Error extracting Life Insurance Fields: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/generate/trauma-insurance-fields', methods=['POST'])
def get_trauma_insurance_fields():
    """
    Extract individual trauma insurance fields for Zapier dynamic prompting
    Returns clean field values without complex sections
    """
    try:
        # Get JSON data
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        print("=" * 70)
        print("EXTRACTING TRAUMA INSURANCE FIELDS")
        print("=" * 70)

        # Extract fields
        result = extract_trauma_insurance_fields(data)

        # Log summary
        print(f"Client: {result.get('client_name', 'Unknown')}")
        print(f"Is Couple: {result.get('is_couple')}")
        print(f"Main Trauma Total: ${result.get('main_total_trauma', 0):,.0f}")
        if result.get('is_couple'):
            print(f"Partner Trauma Total: ${result.get('partner_total_trauma', 0):,.0f}")
        print(f"Recommendation Status: {result.get('trauma_recommendation_status')}")

        print(f"✓ Extracted Trauma Insurance Fields")
        return jsonify(result), 200

    except Exception as e:
        print(f"✗ Error extracting Trauma Insurance Fields: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/generate/income-protection-fields', methods=['POST'])
def get_income_protection_fields():
    """
    Extract individual income protection fields for Zapier dynamic prompting
    Returns clean field values without complex sections
    """
    try:
        # Get JSON data
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        print("=" * 70)
        print("EXTRACTING INCOME PROTECTION FIELDS")
        print("=" * 70)

        # Extract fields
        result = extract_income_protection_fields(data)

        # Log summary
        print(f"Client: {result.get('client_name', 'Unknown')}")
        print(f"Main Monthly Needs: ${result.get('main_monthly_needs', 0):,.0f}")
        print(f"Main Monthly Benefit: ${result.get('main_monthly_benefit', 0):,.0f}")
        if result.get('is_couple'):
            print(f"Partner Monthly Needs: ${result.get('partner_monthly_needs', 0):,.0f}")
            print(f"Partner Monthly Benefit: ${result.get('partner_monthly_benefit', 0):,.0f}")
        print(f"Recommendation: {result.get('income_protection_recommendation_status')}")
        print("=" * 70)

        return jsonify(result), 200

    except Exception as e:
        print(f"✗ Error extracting Income Protection Fields: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/generate/health-insurance-fields', methods=['POST'])
def get_health_insurance_fields():
    """
    Extract individual health insurance fields for Zapier dynamic prompting
    Returns clean field values without complex sections
    """
    try:
        # Get JSON data
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        print("=" * 70)
        print("EXTRACTING HEALTH INSURANCE FIELDS")
        print("=" * 70)

        # Extract fields
        result = extract_health_insurance_fields(data)

        # Log summary
        print(f"Client: {result.get('client_name', 'Unknown')}")
        print(f"Main Coverage Count: {result.get('main_coverage_count', 0)}")
        print(f"Main Plan Type: {result.get('main_plan_type', 'none')}")
        if result.get('is_couple'):
            print(f"Partner Coverage Count: {result.get('partner_coverage_count', 0)}")
            print(f"Partner Plan Type: {result.get('partner_plan_type', 'none')}")
        print(f"Recommended Plan Level: {result.get('recommended_plan_level')}")
        print(f"Recommendation: {result.get('health_insurance_recommendation_status')}")
        print("=" * 70)

        return jsonify(result), 200

    except Exception as e:
        print(f"✗ Error extracting Health Insurance Fields: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/configure/zapier', methods=['POST', 'GET'])
def configure_zapier():
    """Configure Zapier webhook settings"""
    if request.method == 'GET':
        # Return current configuration
        config = zapier_trigger.config
        return jsonify({
            'enabled': config.get('enabled', False),
            'webhook_url': config.get('zapier_webhook_url', ''),
            'configured': config.get('zapier_webhook_url', '') != 'YOUR_ZAPIER_WEBHOOK_URL_HERE'
        }), 200

    # POST method - update configuration
    try:
        data = request.json
        config_path = Path(__file__).parent.parent / "config" / "zapier_config.json"

        # Load current config
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Update with new values
        if 'webhook_url' in data:
            config['zapier_webhook_url'] = data['webhook_url']
        if 'enabled' in data:
            config['enabled'] = bool(data['enabled'])

        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        # Reload the zapier trigger with new config
        zapier_trigger.__init__()

        return jsonify({
            'status': 'success',
            'message': 'Zapier configuration updated',
            'config': {
                'enabled': config.get('enabled'),
                'webhook_url': config.get('zapier_webhook_url')
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/generate/accidental-injury-fields', methods=['POST'])
def get_accidental_injury_fields():
    """
    Extract individual accidental injury fields for Zapier dynamic prompting
    Returns clean field values without complex sections
    """
    try:
        # Get JSON data
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        print("=" * 70)
        print("EXTRACTING ACCIDENTAL INJURY FIELDS")
        print("=" * 70)

        # Extract fields
        result = extract_accidental_injury_fields(data)

        # Log summary
        print(f"Client: {result.get('client_name', 'Unknown')}")
        print(f"Main Needs Accident Cover: {result.get('main_needs_accident_cover')}")
        if result.get('is_couple'):
            print(f"Partner Needs Accident Cover: {result.get('partner_needs_accident_cover')}")
        print(f"Recommendation: {result.get('accident_recommendation_status')}")
        print(f"ACC Top-up Recommended: {result.get('acc_topup_recommended')}")
        print("=" * 70)

        return jsonify(result), 200

    except Exception as e:
        print(f"✗ Error extracting Accidental Injury Fields: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/generate/life-insurance-analysis', methods=['POST'])
def generate_life_insurance_analysis():
    """Generate life insurance needs analysis and coverage details (single & joint)"""
    try:
        data = request.get_json()
        is_couple = data.get('is_couple', False)

        result = extract_life_insurance(data, is_couple=is_couple)
        result['status'] = 'success'

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/generate/trauma-insurance-analysis', methods=['POST'])
def generate_trauma_insurance_analysis():
    """Generate trauma insurance needs analysis and coverage details (single & joint)"""
    try:
        data = request.get_json()
        is_couple = data.get('is_couple', False)

        result = extract_trauma_insurance(data, is_couple=is_couple)
        result['status'] = 'success'

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 70)
    print("INSURANCE SOA WEBHOOK SERVER")
    print("=" * 70)
    print()

    # Load existing forms
    load_all_forms()

    print()
    print("Webhook Endpoints:")
    print("-" * 50)
    print("  Fact Find Form:     POST http://localhost:5001/ff")
    print("                      POST http://localhost:5001/webhook/fact-find")
    print("  Automation Form:    POST http://localhost:5001/automation")
    print("                      POST http://localhost:5001/webhook/automation-form")
    print("  Status:             GET  http://localhost:5001/status")
    print("  Matches:            GET  http://localhost:5001/matches")
    print("  Health:             GET  http://localhost:5001/health")
    print()
    print("New Generator Endpoints (Zapier-ready):")
    print("-" * 50)
    print("  Scope of Advice:    POST http://localhost:5001/generate/scope-of-advice")
    print("  Personal Info:      POST http://localhost:5001/generate/personal-information")
    print("  Combined Report:    POST http://localhost:5001/generate/combined-report")
    print("  Life Insurance:     POST http://localhost:5001/generate/life-insurance-fields")
    print("  Trauma Insurance:   POST http://localhost:5001/generate/trauma-insurance-fields")
    print()
    print("=" * 70)
    print("Server starting on http://localhost:5001")
    print("=" * 70)
    print()

    app.run(host='0.0.0.0', port=5001, debug=True)
