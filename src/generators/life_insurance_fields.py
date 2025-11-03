"""
Life Insurance Fields Extractor - Simplified Text Version with Debugging
"""

from typing import Dict, Any


def extract_life_insurance_fields(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract life insurance fields as simple formatted text blocks
    """

    def safe_int(value: Any, default: int = 0) -> int:
        """Convert to integer, handling currency strings"""
        if not value or value == "":
            return default
        try:
            if isinstance(value, str):
                value = value.replace(',', '').replace(', '').strip()
            n = int(float(value))
            return n if n > 0 else 0
        except (ValueError, TypeError):
            return default

    def format_currency(value: int) -> str:
        """Format as currency"""
        return f"${value:,}"

    # Debug: Print what fields we're checking
    print("=" * 50)
    print("LIFE INSURANCE FIELD EXTRACTION")
    print("=" * 50)
    print("Checking fields:")
    print(f"  Field 380 (Main Debt): {form_data.get('380', 'NOT FOUND')}")
    print(f"  Field 389 (Main Total): {form_data.get('389', 'NOT FOUND')}")
    print(f"  Field 504 (Notes): {form_data.get('504', 'NOT FOUND')[:50] if form_data.get('504') else 'NOT FOUND'}")

    # Determine if couple
    is_couple = form_data.get('is_couple', False) or form_data.get('39') == 'couple'

    # Build main person text block
    main_lines = []
    main_has_data = False

    # Check with both string and numeric field IDs
    # WordPress sometimes sends field IDs as strings with 'f' prefix
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

    # Extract main person fields with multiple ID formats
    fields_main = {
        'Debt Repayment': get_field_value('380'),
        'Income Replacement': get_field_value('381'),
        'Child Education': get_field_value('382'),
        'Final Expenses': get_field_value('383'),
        'Other Considerations': get_field_value('384'),
        'Assets (Offset)': get_field_value('386'),
        'KiwiSaver (Offset)': get_field_value('388'),
        'Total Cover Recommended': get_field_value('389')
    }

    print(f"Main person values found: {fields_main}")

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

        fields_partner = {
            'Debt Repayment': get_field_value('391'),
            'Income Replacement': get_field_value('392'),
            'Child Education': get_field_value('393'),
            'Final Expenses': get_field_value('394'),
            'Other Considerations': get_field_value('395'),
            'Assets (Offset)': get_field_value('397'),
            'KiwiSaver (Offset)': get_field_value('399'),
            'Total Cover Recommended': get_field_value('400')
        }

        print(f"Partner values found: {fields_partner}")

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

    # Extract needs analysis notes - try multiple field formats
    needs_notes = ""
    for field_id in ['504', 'f504', '504.0']:
        notes = str(form_data.get(field_id, '')).strip()
        if notes:
            needs_notes = notes
            break

    if not needs_notes:
        needs_notes = "No additional notes"

    print(f"Final outputs:")
    print(f"  Main text: {len(main_text)} chars")
    print(f"  Partner text: {len(partner_text)} chars")
    print(f"  Notes: {len(needs_notes)} chars")
    print("=" * 50)

    return {
        "client_name": form_data.get('client_name', form_data.get('3', '')),
        "is_couple": is_couple,

        # Three text fields for Zapier
        "life_insurance_main": main_text,
        "life_insurance_partner": partner_text,
        "life_insurance_notes": needs_notes,

        "section_id": "life_insurance",
        "status": "success"
    }
