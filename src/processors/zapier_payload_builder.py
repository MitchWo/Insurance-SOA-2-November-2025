"""
Zapier Payload Builder
Creates standardized, consistent payloads for Zapier webhooks
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path


class ZapierPayloadBuilder:
    """
    Builds standardized Zapier payloads with consistent field structure

    This ensures that every webhook sent to Zapier has the EXACT same structure,
    preventing field mismatches and errors in Zapier workflows.
    """

    def __init__(self):
        """Initialize the payload builder with schema"""
        schema_path = Path(__file__).parent.parent.parent / "config" / "zapier_payload_schema.json"
        try:
            with open(schema_path, 'r') as f:
                self.schema = json.load(f)
        except:
            self.schema = None

    def build_payload(self, combined_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a standardized Zapier payload from combined report data

        Args:
            combined_report: The combined report from auto_matcher

        Returns:
            Standardized payload with guaranteed field structure
        """
        # Extract core fields with fallbacks
        client_email = combined_report.get('email', '')
        client_name = combined_report.get('client_name', 'Unknown Client')
        case_id = combined_report.get('case_id', '')
        is_couple = combined_report.get('is_couple', False)

        # Build the standardized payload - ONLY simple fields + JSON strings for Zapier
        payload = {
            # === CORE IDENTIFICATION (simple fields) ===
            "client_email": client_email,
            "client_name": client_name,
            "partner_name": combined_report.get('partner_name', None),
            "case_id": case_id,
            "is_couple": is_couple,
            "match_confidence": combined_report.get('match_confidence', 0.0),

            # === JSON STRING FIELDS (one field per section - no nested objects!) ===
            "scope_of_advice_json": self._build_section_json(combined_report.get('scope_of_advice', {})),
            "personal_information_json": self._build_section_json(combined_report.get('personal_information', {})),

            # === LIFE INSURANCE (consolidated fields) ===
            "life_insurance_main": combined_report.get('life_insurance', {}).get('life_insurance_main', ''),
            "life_insurance_partner": combined_report.get('life_insurance', {}).get('life_insurance_partner', ''),
            "life_insurance_notes": combined_report.get('life_insurance', {}).get('life_insurance_notes', ''),

            # === TRAUMA INSURANCE (consolidated fields) ===
            "trauma_insurance_main": combined_report.get('trauma_insurance', {}).get('trauma_insurance_main', ''),
            "trauma_insurance_partner": combined_report.get('trauma_insurance', {}).get('trauma_insurance_partner', ''),
            "trauma_insurance_notes": combined_report.get('trauma_insurance', {}).get('trauma_insurance_notes', ''),

            # === OTHER INSURANCE SECTIONS ===
            "income_protection_json": self._build_section_json(combined_report.get('income_protection', {})),
            "health_insurance_json": self._build_section_json(combined_report.get('health_insurance', {})),
            "accidental_injury_json": self._build_section_json(combined_report.get('accidental_injury', {})),

            # === ASSETS & LIABILITIES (simple string fields) ===
            "assets_list": combined_report.get('assets_liabilities', {}).get('assets_json', '[]'),
            "liabilities_list": combined_report.get('assets_liabilities', {}).get('liabilities_json', '[]'),
            "assets_table": combined_report.get('assets_liabilities', {}).get('assets_text', ''),
            "liabilities_table": combined_report.get('assets_liabilities', {}).get('liabilities_text', ''),
            "financial_summary": combined_report.get('assets_liabilities', {}).get('summary_text', ''),
            "total_assets": combined_report.get('assets_liabilities', {}).get('total_assets', 0),
            "total_liabilities": combined_report.get('assets_liabilities', {}).get('total_liabilities', 0),
            "net_worth": combined_report.get('assets_liabilities', {}).get('net_worth', 0),

            # === METADATA ===
            "timestamp": datetime.now().isoformat(),
            "source": "Insurance-SOA-System",
            "payload_version": "1.1"
        }

        return payload

    def _ensure_section(self, section_data: Any, default: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure a section has data, or return a default empty structure

        Args:
            section_data: The section data from combined report
            default: Default structure if section is missing or invalid

        Returns:
            Valid section data or default structure
        """
        if not isinstance(section_data, dict):
            return default

        if not section_data or len(section_data) == 0:
            return default

        # Ensure status is set
        if 'status' not in section_data:
            section_data['status'] = 'success'

        return section_data

    def _build_section_json(self, section_data: Dict[str, Any]) -> str:
        """
        Build a single JSON string field for any insurance section
        for easy Zapier mapping (one field instead of many nested objects)

        Args:
            section_data: The insurance section data from combined report

        Returns:
            JSON string containing all data, or empty object string if not generated
        """
        if not isinstance(section_data, dict) or not section_data:
            return json.dumps({
                "status": "not_generated",
                "message": "Section data not yet generated"
            })

        # If data exists, return it as a JSON string
        return json.dumps(section_data, indent=2)

    def validate_payload(self, payload: Dict[str, Any]) -> tuple[bool, list]:
        """
        Validate that payload matches the schema (simplified for JSON-only structure)

        Args:
            payload: The payload to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required simple fields
        required_fields = [
            'client_email', 'client_name', 'case_id', 'is_couple'
        ]

        for field in required_fields:
            if field not in payload:
                errors.append(f"Missing required field: {field}")

        # Check required JSON fields
        required_json_fields = [
            'scope_of_advice_json', 'personal_information_json',
            'life_insurance_json', 'trauma_insurance_json', 'income_protection_json',
            'health_insurance_json', 'accidental_injury_json'
        ]

        for field in required_json_fields:
            if field not in payload:
                errors.append(f"Missing required JSON field: {field}")
            elif not isinstance(payload.get(field), str):
                errors.append(f"Field '{field}' must be a JSON string")

        # Check types
        if 'is_couple' in payload and not isinstance(payload['is_couple'], bool):
            errors.append("Field 'is_couple' must be boolean")

        if 'match_confidence' in payload and not isinstance(payload['match_confidence'], (int, float)):
            errors.append("Field 'match_confidence' must be number")

        return (len(errors) == 0, errors)

    def get_payload_summary(self, payload: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of the payload (JSON-field version)

        Args:
            payload: The payload to summarize

        Returns:
            Summary string
        """
        summary_lines = [
            f"Client: {payload.get('client_name')} ({payload.get('client_email')})",
            f"Case ID: {payload.get('case_id')}",
            f"Couple: {'Yes' if payload.get('is_couple') else 'No'}",
            f"JSON Fields included:"
        ]

        json_sections = [
            'scope_of_advice_json', 'personal_information_json',
            'life_insurance_json', 'trauma_insurance_json', 'income_protection_json',
            'health_insurance_json', 'accidental_injury_json'
        ]

        for section in json_sections:
            json_data = payload.get(section, '')
            if json_data:
                # Try to parse status from JSON
                try:
                    data = json.loads(json_data)
                    status = data.get('status', 'present')
                except:
                    status = 'present'
            else:
                status = 'missing'
            summary_lines.append(f"  - {section}: {status} ({len(json_data)} chars)")

        return "\n".join(summary_lines)


def build_standardized_payload(combined_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper function to build a standardized payload

    Args:
        combined_report: The combined report from auto_matcher

    Returns:
        Standardized Zapier payload
    """
    builder = ZapierPayloadBuilder()
    return builder.build_payload(combined_report)


if __name__ == "__main__":
    # Test the payload builder
    test_report = {
        "email": "test@example.com",
        "client_name": "John Smith",
        "case_id": "12345",
        "is_couple": False,
        "match_confidence": 0.95,
        "life_insurance": {
            "status": "success",
            "needs_analysis": {"total_needs": 500000}
        }
    }

    builder = ZapierPayloadBuilder()
    payload = builder.build_payload(test_report)

    print("Generated Payload:")
    print(json.dumps(payload, indent=2))

    is_valid, errors = builder.validate_payload(payload)
    print(f"\nValidation: {'PASS' if is_valid else 'FAIL'}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")

    print(f"\nSummary:\n{builder.get_payload_summary(payload)}")
