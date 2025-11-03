"""
Trauma Insurance Fields Extractor - Simplified Text Version
Groups WordPress form fields into text blocks without calculations
"""

from typing import Dict, Any


def extract_trauma_insurance_fields(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract trauma insurance fields as simple formatted text blocks
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

    # Helper to try multiple field ID formats
    def get_field_value(field_id: str) -> int:
        """Try multiple field ID formats"""
        # Try direct numeric
        val = safe_int(form_data.get(field_id, 0))
        if val > 0:
            return val
        # Try with 'f' prefix
        val = safe_int(form_data.get(f'f{field_id}', 0))
        if val > 0:
            return val
        # Try as integer key
        try:
            val = safe_int(form_data.get(int(field_id), 0))
            if val > 0:
                return val
        except:
            pass
        return 0

    # Debug logging
    print("=" * 50)
    print("TRAUMA INSURANCE FIELD EXTRACTION")
    print("=" * 50)
    print("Checking fields:")
    print(f"  Field 402 (Main Income): {form_data.get('402', 'NOT FOUND')}")
    print(f"  Field 409 (Main Total): {form_data.get('409', 'NOT FOUND')}")
    print(f"  Field 506 (Notes): {form_data.get('506', 'NOT FOUND')[:50] if form_data.get('506') else 'NOT FOUND'}")

    # Determine if couple
    is_couple = form_data.get('is_couple', False) or form_data.get('39') == 'couple'

    # Build main person text block
    main_lines = []
    main_has_data = False

    # Extract main person fields directly from form
    fields_main = {
        'Income Replacement': get_field_value('402'),
        'Expense Replacement': get_field_value('486'),
        'Debt Repayment': get_field_value('403'),
        'Medical Bills': get_field_value('404'),
        'Childcare Assistance': get_field_value('405'),
        'Buyback Option': get_field_value('406'),
        'TPD Add-on': get_field_value('407'),
        'Child Trauma Cover': get_field_value('408'),
        'Total Cover Recommended': get_field_value('409')
    }

    print(f"Main person values found: {fields_main}")

    # Build text block - only include non-zero values
    for label, value in fields_main.items():
        if value > 0:
            if not main_has_data:
                main_lines.append("MAIN PERSON TRAUMA INSURANCE")
                main_lines.append("-" * 45)
                main_has_data = True
            main_lines.append(f"{label:<25} {format_currency(value):>15}")

    if main_has_data:
        main_lines.append("-" * 45)

    main_text = "\n".join(main_lines) if main_lines else "No trauma insurance data"

    # Build partner text block if couple
    partner_text = ""

    if is_couple:
        partner_lines = []
        partner_has_data = False

        # Extract partner fields directly from form
        fields_partner = {
            'Income Replacement': get_field_value('411'),
            'Expense Replacement': get_field_value('487'),
            'Debt Repayment': get_field_value('412'),
            'Medical Bills': get_field_value('413'),
            'Childcare Assistance': get_field_value('414'),
            'Buyback Option': get_field_value('415'),
            'TPD Add-on': get_field_value('416'),
            'Child Trauma Cover': get_field_value('417'),
            'Total Cover Recommended': get_field_value('418')
        }

        print(f"Partner values found: {fields_partner}")

        # Build text block - only include non-zero values
        for label, value in fields_partner.items():
            if value > 0:
                if not partner_has_data:
                    partner_lines.append("PARTNER TRAUMA INSURANCE")
                    partner_lines.append("-" * 45)
                    partner_has_data = True
                partner_lines.append(f"{label:<25} {format_currency(value):>15}")

        if partner_has_data:
            partner_lines.append("-" * 45)

        partner_text = "\n".join(partner_lines) if partner_lines else ""

    # Extract needs analysis notes - try multiple field formats for field 506
    needs_notes = ""
    for field_id in ['506', 'f506', '506.0']:
        notes = str(form_data.get(field_id, '')).strip()
        if notes:
            needs_notes = notes
            break

    if not needs_notes:
        needs_notes = "No additional notes"

    # Determine status based on presence of data
    main_needs = fields_main.get('Total Cover Recommended', 0) > 0
    partner_needs = False
    if is_couple:
        partner_needs = fields_partner.get('Total Cover Recommended', 0) > 0

    if main_needs and partner_needs:
        status = "both_need_coverage"
    elif main_needs:
        status = "main_only_needs_coverage"
    elif partner_needs:
        status = "partner_only_needs_coverage"
    else:
        status = "no_coverage_needed"

    print(f"Final outputs:")
    print(f"  Main text: {len(main_text)} chars")
    print(f"  Partner text: {len(partner_text)} chars")
    print(f"  Notes: {len(needs_notes)} chars")
    print("=" * 50)

    return {
        "client_name": form_data.get('client_name', form_data.get('3', '')),
        "is_couple": is_couple,

        # Three simple text fields for Zapier
        "trauma_insurance_main": main_text,
        "trauma_insurance_partner": partner_text,
        "trauma_insurance_notes": needs_notes,

        # Basic status
        "trauma_recommendation_status": status,
        "section_id": "trauma_insurance",
        "status": "success"
    }
