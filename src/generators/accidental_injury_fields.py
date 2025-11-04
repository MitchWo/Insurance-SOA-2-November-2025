"""
Accidental Injury Fields Extractor - Simplified Text Version
Groups WordPress form fields into text blocks without calculations
"""

from typing import Dict, Any


def extract_accidental_injury_fields(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract accidental injury fields as simple formatted text blocks
    No calculations - just format existing field values
    """

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

    def format_yes_no(value: Any) -> str:
        """Format boolean/yes-no field"""
        if not value or value == '':
            return "No"
        val_str = str(value).lower()
        if val_str in ['yes', 'true', '1', 'y', 'relevant', 'needed', 'required']:
            return "Yes"
        return "No"

    # Debug logging
    print("=" * 50)
    print("ACCIDENTAL INJURY FIELD EXTRACTION")
    print("=" * 50)
    print("Checking fields:")
    print(f"  Field 446 (Main Relevant): {form_data.get('446', 'NOT FOUND')}")
    print(f"  Field 447 (Partner Relevant): {form_data.get('447', 'NOT FOUND')}")

    # Determine if couple (check partner fields for data)
    is_couple = form_data.get('is_couple', False) or form_data.get('39') == 'couple'

    # Also check field 39 and 8 for couple detection
    field_39 = form_data.get('39', form_data.get('f39', ''))
    if field_39:
        field_39_str = str(field_39).lower()
        if any(indicator in field_39_str for indicator in ['couple', 'partner', 'yes', 'true', 'my partner and i']):
            is_couple = True
            print(f"  Detected couple due to field 39")

    field_8 = form_data.get('8', form_data.get('f8', ''))
    if field_8:
        field_8_str = str(field_8).lower()
        if any(status in field_8_str for status in ['married', 'defacto', 'de facto', 'civil union', 'partner', 'couple']):
            is_couple = True
            print(f"  Detected couple due to field 8")

    # Check if partner field has value
    if get_field_value('447'):
        is_couple = True
        print(f"  Detected couple due to partner field 447 having value")

    print(f"Is Couple: {is_couple}")

    # Build main person text block
    main_lines = []
    main_has_data = False

    # Extract main person field
    main_relevant = get_field_value('446')
    main_formatted = format_yes_no(main_relevant)

    if main_formatted == "Yes":
        main_has_data = True
        main_lines.append("MAIN PERSON ACCIDENTAL INJURY")
        main_lines.append("-" * 45)
        main_lines.append(f"{'Accident Cover Relevant':<25} {'Yes':>15}")
        main_lines.append("-" * 45)

    main_text = "\n".join(main_lines) if main_lines else "No accidental injury coverage needed"

    # Build partner text block
    partner_text = ""
    partner_lines = []
    partner_has_data = False

    if is_couple:
        partner_relevant = get_field_value('447')
        partner_formatted = format_yes_no(partner_relevant)

        if partner_formatted == "Yes":
            partner_has_data = True
            partner_lines.append("PARTNER ACCIDENTAL INJURY")
            partner_lines.append("-" * 45)
            partner_lines.append(f"{'Accident Cover Relevant':<25} {'Yes':>15}")
            partner_lines.append("-" * 45)

        partner_text = "\n".join(partner_lines) if partner_lines else ""

    # No dedicated notes field for accidental injury
    needs_notes = "No additional notes"

    # Determine status based on presence of data
    if main_has_data and partner_has_data:
        status = "both_need_coverage"
    elif main_has_data:
        status = "main_only_needs_coverage"
    elif partner_has_data:
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
        "accidental_injury_main": main_text,
        "accidental_injury_partner": partner_text,
        "accidental_injury_notes": needs_notes,

        # Basic status
        "accidental_injury_recommendation_status": status,
        "section_id": "accidental_injury",
        "status": "success"
    }
