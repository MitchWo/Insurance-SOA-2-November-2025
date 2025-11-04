"""
Health Insurance Fields Extractor - Simplified Text Version
Groups WordPress form fields into text blocks without calculations
"""

from typing import Dict, Any


def extract_health_insurance_fields(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract health insurance fields as simple formatted text blocks
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

    def get_field_value(field_id: str) -> Any:
        """Try multiple field ID formats and return raw value"""
        # Try direct numeric
        val = form_data.get(field_id)
        if val is not None and val != '':
            return val
        # Try with 'f' prefix
        val = form_data.get(f'f{field_id}')
        if val is not None and val != '':
            return val
        # Try as integer key
        try:
            val = form_data.get(int(field_id))
            if val is not None and val != '':
                return val
        except:
            pass
        return None

    def get_int_field(field_id: str) -> int:
        """Get field value as integer"""
        val = get_field_value(field_id)
        return safe_int(val, 0)

    def get_str_field(field_id: str) -> str:
        """Get field value as string"""
        val = get_field_value(field_id)
        return str(val) if val else ""

    def format_yes_no(value: Any) -> str:
        """Format boolean/yes-no field"""
        if not value or value == '':
            return "No"
        val_str = str(value).lower()
        if val_str in ['yes', 'true', '1', 'y']:
            return "Yes"
        return "No"

    # Debug logging
    print("=" * 50)
    print("HEALTH INSURANCE FIELD EXTRACTION")
    print("=" * 50)
    print("Checking fields:")
    print(f"  Field 449 (Main Private Care): {form_data.get('449', 'NOT FOUND')}")
    print(f"  Field 453 (Main Base Excess): {form_data.get('453', 'NOT FOUND')}")
    print(f"  Field 510 (Notes): {form_data.get('510', 'NOT FOUND')[:50] if form_data.get('510') else 'NOT FOUND'}")

    # Determine if couple (check partner fields for data)
    is_couple = form_data.get('is_couple', False) or form_data.get('39') == 'couple'

    # Also check if any partner health insurance fields have values
    partner_field_ids = ['456', '457', '458', '459', '460', '461']
    for field_id in partner_field_ids:
        if get_field_value(field_id):
            is_couple = True
            print(f"  Detected couple due to partner field {field_id} having value")
            break

    print(f"Is Couple: {is_couple}")

    # Build main person text block
    main_lines = []
    main_has_data = False

    # Extract main person fields
    fields_to_extract = [
        ('Private Care Access', '449', 'yes_no'),
        ('Specialists/Tests', '450', 'yes_no'),
        ('Non-Pharmac Drugs', '451', 'yes_no'),
        ('Dental/Optical/Physio', '452', 'yes_no'),
        ('Base Excess', '453', 'currency'),
        ('Child Coverage', '454', 'yes_no')
    ]

    # Build text for main person
    for label, field_id, field_type in fields_to_extract:
        if field_type == 'currency':
            value = get_int_field(field_id)
            if value > 0:
                if not main_has_data:
                    main_lines.append("MAIN PERSON HEALTH INSURANCE")
                    main_lines.append("-" * 45)
                    main_has_data = True
                main_lines.append(f"{label:<25} {format_currency(value):>15}")
        elif field_type == 'yes_no':
            value = get_field_value(field_id)
            formatted = format_yes_no(value)
            if formatted == "Yes":  # Only show if Yes
                if not main_has_data:
                    main_lines.append("MAIN PERSON HEALTH INSURANCE")
                    main_lines.append("-" * 45)
                    main_has_data = True
                main_lines.append(f"{label:<25} {formatted:>15}")
        else:  # text
            value = get_str_field(field_id)
            if value:
                if not main_has_data:
                    main_lines.append("MAIN PERSON HEALTH INSURANCE")
                    main_lines.append("-" * 45)
                    main_has_data = True
                main_lines.append(f"{label:<25} {value:>15}")

    if main_has_data:
        main_lines.append("-" * 45)

    main_text = "\n".join(main_lines) if main_lines else "No health insurance data"

    # Build partner text block
    partner_text = ""
    partner_lines = []
    partner_has_data = False

    if is_couple:
        # Extract partner fields
        partner_fields = [
            ('Private Care Access', '456', 'yes_no'),
            ('Specialists/Tests', '457', 'yes_no'),
            ('Non-Pharmac Drugs', '458', 'yes_no'),
            ('Dental/Optical/Physio', '459', 'yes_no'),
            ('Base Excess', '460', 'currency'),
            ('Child Coverage', '461', 'yes_no')
        ]

        # Build text for partner
        for label, field_id, field_type in partner_fields:
            if field_type == 'currency':
                value = get_int_field(field_id)
                if value > 0:
                    if not partner_has_data:
                        partner_lines.append("PARTNER HEALTH INSURANCE")
                        partner_lines.append("-" * 45)
                        partner_has_data = True
                    partner_lines.append(f"{label:<25} {format_currency(value):>15}")
            elif field_type == 'yes_no':
                value = get_field_value(field_id)
                formatted = format_yes_no(value)
                if formatted == "Yes":  # Only show if Yes
                    if not partner_has_data:
                        partner_lines.append("PARTNER HEALTH INSURANCE")
                        partner_lines.append("-" * 45)
                        partner_has_data = True
                    partner_lines.append(f"{label:<25} {formatted:>15}")
            else:  # text
                value = get_str_field(field_id)
                if value:
                    if not partner_has_data:
                        partner_lines.append("PARTNER HEALTH INSURANCE")
                        partner_lines.append("-" * 45)
                        partner_has_data = True
                    partner_lines.append(f"{label:<25} {value:>15}")

        if partner_has_data:
            partner_lines.append("-" * 45)

        partner_text = "\n".join(partner_lines) if partner_lines else ""

    # Extract needs analysis notes - try multiple field formats for field 510
    needs_notes = ""
    for field_id in ['510', 'f510', '510.0']:
        notes = str(form_data.get(field_id, '')).strip()
        if notes:
            needs_notes = notes
            break

    if not needs_notes:
        needs_notes = "No additional notes"

    # Determine status based on presence of data
    main_needs = main_has_data
    partner_needs = partner_has_data

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
        "health_insurance_main": main_text,
        "health_insurance_partner": partner_text,
        "health_insurance_notes": needs_notes,

        # Basic status
        "health_insurance_recommendation_status": status,
        "section_id": "health_insurance",
        "status": "success"
    }
