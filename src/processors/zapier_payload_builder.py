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

        # Build the standardized payload
        payload = {
            # === CORE IDENTIFICATION ===
            "client_email": client_email,
            "client_name": client_name,
            "partner_name": combined_report.get('partner_name', None),
            "case_id": case_id,
            "is_couple": is_couple,
            "match_confidence": combined_report.get('match_confidence', 0.0),

            # === SCOPE OF ADVICE ===
            "scope_of_advice": self._ensure_section(
                combined_report.get('scope_of_advice', {}),
                {
                    "status": "not_generated",
                    "products_in_scope": [],
                    "products_out_of_scope": [],
                    "limitations": ""
                }
            ),

            # === PERSONAL INFORMATION ===
            "personal_information": self._ensure_section(
                combined_report.get('personal_information', {}),
                {
                    "status": "not_generated",
                    "household": {"people": []}
                }
            ),

            # === ASSETS & LIABILITIES ===
            "assets_liabilities": self._ensure_section(
                combined_report.get('assets_liabilities', {}),
                {
                    "status": "not_generated",
                    "total_assets": 0,
                    "total_liabilities": 0,
                    "net_worth": 0
                }
            ),

            # === ASSETS & LIABILITIES JSON (single field for Zapier mapping) ===
            "assets_liabilities_json": self._build_assets_liabilities_json(
                combined_report.get('assets_liabilities', {})
            ),

            # === LIFE INSURANCE ===
            "life_insurance": self._ensure_section(
                combined_report.get('life_insurance', {}),
                {
                    "status": "not_generated",
                    "needs_analysis": {},
                    "coverage": {}
                }
            ),

            # === TRAUMA INSURANCE ===
            "trauma_insurance": self._ensure_section(
                combined_report.get('trauma_insurance', {}),
                {
                    "status": "not_generated",
                    "needs_analysis": {},
                    "coverage": {}
                }
            ),

            # === INCOME PROTECTION ===
            "income_protection": self._ensure_section(
                combined_report.get('income_protection', {}),
                {
                    "status": "not_generated",
                    "needs_analysis": {},
                    "coverage": {}
                }
            ),

            # === HEALTH INSURANCE ===
            "health_insurance": self._ensure_section(
                combined_report.get('health_insurance', {}),
                {
                    "status": "not_generated",
                    "needs_analysis": {},
                    "coverage": {}
                }
            ),

            # === ACCIDENTAL INJURY / ACC ===
            "accidental_injury": self._ensure_section(
                combined_report.get('accidental_injury', {}),
                {
                    "status": "not_generated",
                    "needs_analysis": {},
                    "coverage": {}
                }
            ),

            # === METADATA ===
            "timestamp": datetime.now().isoformat(),
            "source": "Insurance-SOA-System",
            "payload_version": "1.0"
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

    def _build_assets_liabilities_json(self, assets_data: Dict[str, Any]) -> str:
        """
        Build a single JSON string field containing all assets & liabilities data
        for easy Zapier mapping (one field instead of many nested objects)

        Args:
            assets_data: The assets_liabilities data from combined report

        Returns:
            JSON string containing all data, or empty object string if not generated
        """
        if not isinstance(assets_data, dict) or not assets_data:
            return json.dumps({
                "status": "not_generated",
                "message": "Assets & liabilities data not yet generated"
            })

        # If data exists, return it as a JSON string
        return json.dumps(assets_data, indent=2)

    def validate_payload(self, payload: Dict[str, Any]) -> tuple[bool, list]:
        """
        Validate that payload matches the schema

        Args:
            payload: The payload to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        required_fields = [
            'client_email', 'client_name', 'case_id', 'is_couple',
            'scope_of_advice', 'personal_information', 'life_insurance',
            'trauma_insurance', 'income_protection', 'health_insurance',
            'accidental_injury'
        ]

        for field in required_fields:
            if field not in payload:
                errors.append(f"Missing required field: {field}")

        # Check types
        if 'is_couple' in payload and not isinstance(payload['is_couple'], bool):
            errors.append("Field 'is_couple' must be boolean")

        if 'match_confidence' in payload and not isinstance(payload['match_confidence'], (int, float)):
            errors.append("Field 'match_confidence' must be number")

        # Check that all insurance sections are dicts
        insurance_sections = [
            'scope_of_advice', 'personal_information', 'assets_liabilities',
            'life_insurance', 'trauma_insurance', 'income_protection',
            'health_insurance', 'accidental_injury'
        ]

        for section in insurance_sections:
            if section in payload and not isinstance(payload[section], dict):
                errors.append(f"Field '{section}' must be object/dict")

        return (len(errors) == 0, errors)

    def get_payload_summary(self, payload: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of the payload

        Args:
            payload: The payload to summarize

        Returns:
            Summary string
        """
        summary_lines = [
            f"Client: {payload.get('client_name')} ({payload.get('client_email')})",
            f"Case ID: {payload.get('case_id')}",
            f"Couple: {'Yes' if payload.get('is_couple') else 'No'}",
            f"Sections included:"
        ]

        sections = [
            'scope_of_advice', 'personal_information', 'assets_liabilities',
            'life_insurance', 'trauma_insurance', 'income_protection',
            'health_insurance', 'accidental_injury'
        ]

        for section in sections:
            data = payload.get(section, {})
            status = data.get('status', 'missing') if isinstance(data, dict) else 'invalid'
            summary_lines.append(f"  - {section}: {status}")

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
