"""
Personal Information Extractor - Text Format Version
Extracts personal information as formatted text table for Zapier
"""

from typing import Dict, Any, Optional
from datetime import datetime
import re


def extract_personal_information(combined_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract personal information as a formatted text table
    Single text field for Zapier instead of parsed JSON
    """

    def safe_get(data: dict, field: str, default: Any = "") -> Any:
        """Safely get a field value with a default"""
        return data.get(field, default) if data else default

    def safe_int(value: Any, default: int = 0) -> int:
        """Convert to integer, handling currency strings"""
        if not value or value == "":
            return default
        if isinstance(value, (int, float)):
            return max(0, int(value))
        cleaned = str(value).replace(', ', '').replace(',', '').strip()
        try:
            return max(0, int(float(cleaned)))
        except:
            return default

    def format_currency(value: int) -> str:
        """Format as currency"""
        return f"${value:,}" if value > 0 else "$0"

    def calculate_age(dob_string: str) -> int:
        """Calculate age from date of birth string"""
        if not dob_string or dob_string == "":
            return 0
        try:
            for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    dob = datetime.strptime(dob_string, fmt)
                    today = datetime.now()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    return int(age)
                except ValueError:
                    continue
            return 0
        except:
            return 0

    def get_employment_status(is_self_employed: bool, hours_field: str, combined_data: Dict) -> str:
        """Determine employment status"""
        if is_self_employed:
            return "Self-Employed"
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
        return "Fulltime"

    # Build text table for personal information
    lines = []
    lines.append("PERSONAL INFORMATION")
    lines.append("=" * 60)

    # Main person information
    main_first = safe_get(combined_data, "144") or safe_get(combined_data, "first_name") or ""
    main_last = safe_get(combined_data, "145", "")
    main_name = f"{main_first} {main_last}".strip() or "Main Person"

    main_age = calculate_age(safe_get(combined_data, "94", safe_get(combined_data, "95", "")))
    main_occupation = safe_get(combined_data, "6", "")
    main_employer = safe_get(combined_data, "277", "")
    main_salary = safe_int(safe_get(combined_data, "10", 0))

    # Check if self-employed
    main_self_employed = str(safe_get(combined_data, "276", "")).lower() in ['yes', 'true', '1']
    if main_self_employed:
        main_employer = "Self-Employed"

    main_status = get_employment_status(main_self_employed, "275", combined_data)

    # Will/EPA status
    will_status = safe_get(combined_data, "26", "")
    if str(will_status).lower() in ['yes', 'true', '1']:
        will_text = "In Place"
    elif str(will_status).lower() in ['no', 'false', '0']:
        will_text = "Not In Place"
    else:
        will_text = "Not Specified"

    # Add main person to table
    lines.append("")
    lines.append("Main Person:")
    lines.append("-" * 40)
    lines.append(f"Name:                {main_name}")
    if main_age > 0:
        lines.append(f"Age:                 {main_age} years")
    if main_occupation:
        lines.append(f"Occupation:          {main_occupation}")
    if main_employer:
        lines.append(f"Employer:            {main_employer}")
    if main_salary > 0:
        lines.append(f"Annual Salary:       {format_currency(main_salary)}")
    lines.append(f"Employment Status:   {main_status}")
    lines.append(f"Will/EPA:            {will_text}")

    # Check for partner
    partner_first = safe_get(combined_data, "146", "")
    partner_last = safe_get(combined_data, "147", "")

    # Determine if couple
    is_couple = bool(partner_first or partner_last)
    if not is_couple:
        # Also check couple indicators
        couple_field = str(safe_get(combined_data, "39", safe_get(combined_data, "8", ""))).lower()
        if 'couple' in couple_field or 'partner' in couple_field:
            is_couple = True

    if is_couple:
        partner_name = f"{partner_first} {partner_last}".strip() or "Partner"
        partner_age = calculate_age(safe_get(combined_data, "95", ""))
        partner_occupation = safe_get(combined_data, "40", safe_get(combined_data, "286", ""))
        partner_employer = safe_get(combined_data, "297", safe_get(combined_data, "288", ""))
        partner_salary = safe_int(safe_get(combined_data, "42", safe_get(combined_data, "296", 0)))

        # Check if partner is self-employed
        partner_self_employed = str(safe_get(combined_data, "483", "")).lower() in ['yes', 'true', '1']
        if partner_self_employed:
            partner_employer = "Self-Employed"

        partner_status = get_employment_status(partner_self_employed, "295", combined_data)

        # Partner Will/EPA status
        partner_will = safe_get(combined_data, "300", "")
        if str(partner_will).lower() in ['yes', 'true', '1']:
            partner_will_text = "In Place"
        elif str(partner_will).lower() in ['no', 'false', '0']:
            partner_will_text = "Not In Place"
        else:
            partner_will_text = "Not Specified"

        # Add partner to table
        lines.append("")
        lines.append("Partner:")
        lines.append("-" * 40)
        lines.append(f"Name:                {partner_name}")
        if partner_age > 0:
            lines.append(f"Age:                 {partner_age} years")
        if partner_occupation:
            lines.append(f"Occupation:          {partner_occupation}")
        if partner_employer:
            lines.append(f"Employer:            {partner_employer}")
        if partner_salary > 0:
            lines.append(f"Annual Salary:       {format_currency(partner_salary)}")
        lines.append(f"Employment Status:   {partner_status}")
        lines.append(f"Will/EPA:            {partner_will_text}")

    # Add summary
    lines.append("")
    lines.append("=" * 60)
    total_income = main_salary + (safe_int(safe_get(combined_data, "42", 0)) if is_couple else 0)
    if total_income > 0:
        lines.append(f"Combined Annual Income: {format_currency(total_income)}")

    # Create the final text block
    personal_info_text = "\n".join(lines)

    # Debug output
    print("=" * 50)
    print("PERSONAL INFORMATION EXTRACTION")
    print("=" * 50)
    print(f"Is Couple: {is_couple}")
    print(f"Main Name: {main_name}")
    print(f"Partner Name: {partner_name if is_couple else 'N/A'}")
    print(f"Text Length: {len(personal_info_text)} chars")
    print("=" * 50)

    return {
        "section_id": "personal_information",
        "personal_information_text": personal_info_text,
        "is_couple": is_couple,
        "status": "success"
    }
