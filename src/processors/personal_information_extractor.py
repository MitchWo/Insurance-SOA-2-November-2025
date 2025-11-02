"""
Personal Information Extractor
Extracts personal information in simple table format for Zapier consumption
Replaces the old where_are_you_now generator with cleaner data extraction
"""

from typing import Dict, Any, Optional
from datetime import datetime


def extract_personal_information(combined_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract personal information in a compact structured format for Zapier.

    Args:
        combined_data: Combined fact find and automation form data

    Returns:
        Dictionary with personal information in compact household format
    """

    def safe_get(data: dict, field: str, default: Any = "") -> Any:
        """Safely get a field value with a default"""
        return data.get(field, default) if data else default

    def calculate_age(dob_string: str) -> int:
        """Calculate age from date of birth string, return integer"""
        if not dob_string or dob_string == "":
            return 0
        try:
            # Handle various date formats (MM/DD/YYYY or YYYY-MM-DD)
            for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"]:
                try:
                    dob = datetime.strptime(dob_string, fmt)
                    today = datetime.now()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    return int(age)  # Return integer
                except ValueError:
                    continue
            return 0
        except:
            return 0

    def clean_salary_to_int(value: Any) -> int:
        """Clean salary and convert to integer NZD (no decimals)"""
        if not value or value == "":
            return 0
        if isinstance(value, (int, float)):
            return int(value)  # Floor decimals
        # Remove $, commas, and convert to int
        cleaned = str(value).replace('$', '').replace(',', '').strip()
        try:
            return int(float(cleaned))  # Convert to float first then int to handle decimals
        except:
            return 0

    def get_employment_status(is_self_employed: bool, hours_field: str, combined_data: Dict) -> str:
        """Determine employment status based on form data"""
        if is_self_employed:
            return "Self-Employed"

        # Check hours worked to determine full/part time
        hours = safe_get(combined_data, hours_field, "")
        if hours:
            try:
                hours_num = float(hours)
                if hours_num >= 30:
                    return "Fulltime"
                elif hours_num > 0:
                    return "Part-time"
            except:
                pass

        # Default to Fulltime if employed but hours not specified
        return "Fulltime"

    def get_will_status(will_field_value: Any) -> str:
        """Convert will field value to standardized status"""
        if not will_field_value or will_field_value == "":
            return ""

        value_lower = str(will_field_value).lower()
        if value_lower in ['yes', 'true', '1', 'in place']:
            return "In Place"
        elif value_lower in ['no', 'false', '0', 'none']:
            return "Not In Place"
        else:
            return ""

    # Initialize household array
    people = []

    # Extract main contact information
    main_name_first = safe_get(combined_data, "144", safe_get(combined_data, "3", ""))
    main_name_last = safe_get(combined_data, "145", "")
    main_full_name = f"{main_name_first} {main_name_last}".strip()

    # Use first name as label, or "Client" if missing
    main_label = main_name_first if main_name_first else "Client"

    # Check if self-employed
    main_is_self_employed = safe_get(combined_data, "276") in ["Yes", "true", "1", True]
    main_employer = safe_get(combined_data, "277", "")

    # If self-employed flag is set or no employer specified, set employer to "Self-Employed"
    if main_is_self_employed or not main_employer:
        main_employer = "Self-Employed"

    # Build main person object
    main_person = {
        "label": main_label,
        "age": calculate_age(safe_get(combined_data, "94", safe_get(combined_data, "95", ""))),
        "occupation": safe_get(combined_data, "6", ""),
        "employer": main_employer,
        "salary_before_tax_nzd": clean_salary_to_int(safe_get(combined_data, "10", 0)),
        "employment_status": get_employment_status(main_is_self_employed, "275", combined_data),
        "will_epa_status": get_will_status(safe_get(combined_data, "26", ""))
    }

    people.append(main_person)

    # Check if this is a couple
    partner_name_first = safe_get(combined_data, "146", "")
    partner_name_last = safe_get(combined_data, "147", "")
    partner_full_name = f"{partner_name_first} {partner_name_last}".strip()
    is_couple = bool(partner_full_name) or safe_get(combined_data, "39") == "couple" or safe_get(combined_data, "8") == "My partner and I"

    # Add partner if couple
    if is_couple:
        # Use first name as label, or "Partner" if missing
        partner_label = partner_name_first if partner_name_first else "Partner"

        # Check if partner is self-employed
        partner_is_self_employed = safe_get(combined_data, "483") in ["Yes", "true", "1", True]
        partner_employer = safe_get(combined_data, "297", safe_get(combined_data, "288", ""))

        # If self-employed flag is set or no employer specified, set employer to "Self-Employed"
        if partner_is_self_employed or not partner_employer:
            partner_employer = "Self-Employed"

        partner_person = {
            "label": partner_label,
            "age": calculate_age(safe_get(combined_data, "95", "")),
            "occupation": safe_get(combined_data, "40", safe_get(combined_data, "286", "")),
            "employer": partner_employer,
            "salary_before_tax_nzd": clean_salary_to_int(safe_get(combined_data, "42", safe_get(combined_data, "296", 0))),
            "employment_status": get_employment_status(partner_is_self_employed, "295", combined_data),
            "will_epa_status": get_will_status(safe_get(combined_data, "300", ""))
        }

        people.append(partner_person)

    # Build the compact payload
    result = {
        "section_id": "personal_information",
        "household": {
            "people": people
        },
        "format": {
            "currency": "NZD",
            "locale": "en-NZ"
        },
        "constraints": {
            "max_chars": 360
        }
    }

    return result