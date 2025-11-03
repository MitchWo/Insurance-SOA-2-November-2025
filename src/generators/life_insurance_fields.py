"""
Life Insurance Fields Extractor - Simple Text Version
Groups WordPress form fields into text blocks without calculations
"""

from typing import Dict, Any


def extract_life_insurance_fields(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract life insurance fields as simple formatted text blocks
    No calculations - just format existing field values
    """

    def safe_int(value: Any, default: int = 0) -> int:
        """Convert to integer, handling currency strings"""
        if not value or value == "":
            return default
        try:
            if isinstance(value, str):
                value = value.replace(',', '').replace(', ', '').strip()
            n = int(float(value))
            return n if n > 0 else 0
        except (ValueError, TypeError):
            return default

    def format_currency(value: int) -> str:
        """Format as currency"""
        return f"${value:,}"

    # Determine if couple
    is_couple = form_data.get('is_couple', False) or form_data.get('39') == 'couple'

    # Build main person text block from raw fields
    main_lines = []
    main_has_data = False

    # Extract field values directly - no calculations
    fields_main = {
        'Debt Repayment': safe_int(form_data.get('380', 0)),
        'Income Replacement': safe_int(form_data.get('381', 0)),
        'Child Education': safe_int(form_data.get('382', 0)),
        'Final Expenses': safe_int(form_data.get('383', 0)),
        'Other Considerations': safe_int(form_data.get('384', 0)),
        'Assets (Offset)': safe_int(form_data.get('386', 0)),
        'KiwiSaver (Offset)': safe_int(form_data.get('388', 0)),
        'Total Cover Recommended': safe_int(form_data.get('389', 0))
    }

    # Build text block - only include non-zero values
    for label, value in fields_main.items():
        if value > 0:
            if not main_has_data:
                main_lines.append("MAIN PERSON LIFE INSURANCE")
                main_lines.append("-" * 45)
                main_has_data = True
            main_lines.append(f"{label:<25} {format_currency(value):>15}")

    if main_has_data:
        main_lines.append("-" * 45)

    main_text = "\n".join(main_lines) if main_lines else "No life insurance data"

    # Build partner text block if couple
    partner_text = ""

    if is_couple:
        partner_lines = []
        partner_has_data = False

        # Extract partner field values directly
        fields_partner = {
            'Debt Repayment': safe_int(form_data.get('391', 0)),
            'Income Replacement': safe_int(form_data.get('392', 0)),
            'Child Education': safe_int(form_data.get('393', 0)),
            'Final Expenses': safe_int(form_data.get('394', 0)),
            'Other Considerations': safe_int(form_data.get('395', 0)),
            'Assets (Offset)': safe_int(form_data.get('397', 0)),
            'KiwiSaver (Offset)': safe_int(form_data.get('399', 0)),
            'Total Cover Recommended': safe_int(form_data.get('400', 0))
        }

        # Build text block - only include non-zero values
        for label, value in fields_partner.items():
            if value > 0:
                if not partner_has_data:
                    partner_lines.append("PARTNER LIFE INSURANCE")
                    partner_lines.append("-" * 45)
                    partner_has_data = True
                partner_lines.append(f"{label:<25} {format_currency(value):>15}")

        if partner_has_data:
            partner_lines.append("-" * 45)

        partner_text = "\n".join(partner_lines) if partner_lines else ""

    # Extract needs analysis notes (field 504)
    needs_notes = str(form_data.get('504', '')).strip()
    if not needs_notes:
        needs_notes = ""

    # Determine if coverage is needed based on presence of data
    main_needs = fields_main.get('Total Cover Recommended', 0) > 0
    partner_needs = False
    if is_couple:
        partner_needs = fields_partner.get('Total Cover Recommended', 0) > 0

    # Simple status
    if main_needs and partner_needs:
        status = "both_need_coverage"
    elif main_needs:
        status = "main_only_needs_coverage"
    elif partner_needs:
        status = "partner_only_needs_coverage"
    else:
        status = "no_coverage_needed"

    return {
        "client_name": form_data.get('client_name', form_data.get('3', '')),
        "is_couple": is_couple,

        # Three simple text fields for Zapier
        "life_insurance_main": main_text,
        "life_insurance_partner": partner_text,
        "life_insurance_notes": needs_notes,

        # Basic status
        "recommendation_status": status,
        "section_id": "life_insurance",
        "status": "success"
    }
