"""
Life Insurance Extractor

Extracts life insurance information with separate sections for:
1. Needs Analysis (narrative/context for why life insurance is needed)
2. Individual Coverage Details (single person coverage)
3. Joint Coverage Details (couple coverage with cross-ownership considerations)

Designed for Zapier consumption with clean, structured data
"""

from typing import Dict, Any, Optional, List


def extract_life_insurance(combined_data: Dict[str, Any], is_couple: bool = False) -> Dict[str, Any]:
    """
    Extract life insurance information separating needs analysis from coverage fields.

    Args:
        combined_data: Combined fact find and automation form data
        is_couple: Whether this is for a couple (affects structure)

    Returns:
        Dictionary with life insurance needs analysis and coverage details
    """

    def safe_get(data: dict, field: str, default: Any = "") -> Any:
        """Safely get a field value with a default"""
        return data.get(field, default) if data else default

    def clean_currency(value: Any) -> int:
        """Convert currency values to integer (NZD)"""
        if not value or value == "":
            return 0
        if isinstance(value, (int, float)):
            return int(value)
        cleaned = str(value).replace('$', '').replace(',', '').strip()
        try:
            return int(float(cleaned))
        except:
            return 0

    def format_currency(value: int) -> str:
        """Format integer as currency string"""
        return f"${value:,}" if value > 0 else "$0"

    # Extract needs analysis (narrative section)
    needs_analysis = safe_get(combined_data, "504", "")

    # Main person life insurance fields
    main_sum_insured = clean_currency(safe_get(combined_data, "389", 0))
    main_existing_cover = clean_currency(safe_get(combined_data, "380", 0))
    main_life_insurance_selected = safe_get(combined_data, "520.1", "") == "Life Insurance"

    # Partner person life insurance fields
    partner_sum_insured = clean_currency(safe_get(combined_data, "400", 0))
    partner_existing_cover = clean_currency(safe_get(combined_data, "391", 0))
    partner_life_insurance_selected = safe_get(combined_data, "520.1", "") == "Life Insurance"

    # Build response based on couple status
    if is_couple:
        result = {
            "section_id": "life_insurance",
            "section_type": "life_insurance_couple",
            "scenario": "joint",
            "needs_analysis": {
                "narrative": needs_analysis,
                "context": "Cross-ownership business considerations",
                "applies_to": "both_partners"
            },
            "coverage": {
                "primary": {
                    "person": "Main Person",
                    "sum_insured_nzd": main_sum_insured,
                    "sum_insured_formatted": format_currency(main_sum_insured),
                    "existing_cover_nzd": main_existing_cover,
                    "existing_cover_formatted": format_currency(main_existing_cover),
                    "shortfall_nzd": max(0, main_sum_insured - main_existing_cover),
                    "shortfall_formatted": format_currency(max(0, main_sum_insured - main_existing_cover)),
                    "is_in_scope": main_life_insurance_selected
                },
                "secondary": {
                    "person": "Partner",
                    "sum_insured_nzd": partner_sum_insured,
                    "sum_insured_formatted": format_currency(partner_sum_insured),
                    "existing_cover_nzd": partner_existing_cover,
                    "existing_cover_formatted": format_currency(partner_existing_cover),
                    "shortfall_nzd": max(0, partner_sum_insured - partner_existing_cover),
                    "shortfall_formatted": format_currency(max(0, partner_sum_insured - partner_existing_cover)),
                    "is_in_scope": partner_life_insurance_selected
                }
            },
            "format": {
                "currency": "NZD",
                "locale": "en-NZ"
            }
        }
    else:
        # Single person scenario
        result = {
            "section_id": "life_insurance",
            "section_type": "life_insurance_single",
            "scenario": "single",
            "needs_analysis": {
                "narrative": needs_analysis,
                "context": "Individual protection needs",
                "applies_to": "individual"
            },
            "coverage": {
                "person": {
                    "sum_insured_nzd": main_sum_insured,
                    "sum_insured_formatted": format_currency(main_sum_insured),
                    "existing_cover_nzd": main_existing_cover,
                    "existing_cover_formatted": format_currency(main_existing_cover),
                    "shortfall_nzd": max(0, main_sum_insured - main_existing_cover),
                    "shortfall_formatted": format_currency(max(0, main_sum_insured - main_existing_cover)),
                    "is_in_scope": main_life_insurance_selected
                }
            },
            "format": {
                "currency": "NZD",
                "locale": "en-NZ"
            }
        }

    return result


def extract_trauma_insurance(combined_data: Dict[str, Any], is_couple: bool = False) -> Dict[str, Any]:
    """
    Extract trauma insurance information separating needs analysis from coverage fields.

    Args:
        combined_data: Combined fact find and automation form data
        is_couple: Whether this is for a couple

    Returns:
        Dictionary with trauma insurance needs analysis and coverage details
    """

    def safe_get(data: dict, field: str, default: Any = "") -> Any:
        """Safely get a field value with a default"""
        return data.get(field, default) if data else default

    def clean_currency(value: Any) -> int:
        """Convert currency values to integer"""
        if not value or value == "":
            return 0
        if isinstance(value, (int, float)):
            return int(value)
        cleaned = str(value).replace('$', '').replace(',', '').strip()
        try:
            return int(float(cleaned))
        except:
            return 0

    def format_currency(value: int) -> str:
        """Format integer as currency string"""
        return f"${value:,}" if value > 0 else "$0"

    # Extract needs analysis
    needs_analysis = safe_get(combined_data, "506", "")

    # Trauma insurance fields
    main_trauma_sum = clean_currency(safe_get(combined_data, "409", 0))
    main_trauma_existing = clean_currency(safe_get(combined_data, "405", 0))
    main_trauma_selected = safe_get(combined_data, "520.3", "") in ["Trauma Cover", "Trauma"]

    partner_trauma_sum = clean_currency(safe_get(combined_data, "418", 0))
    partner_trauma_existing = clean_currency(safe_get(combined_data, "414", 0))
    partner_trauma_selected = safe_get(combined_data, "520.3", "") in ["Trauma Cover", "Trauma"]

    if is_couple:
        result = {
            "section_id": "trauma_insurance",
            "section_type": "trauma_insurance_couple",
            "scenario": "joint",
            "needs_analysis": {
                "narrative": needs_analysis,
                "context": "Protection against serious illness",
                "applies_to": "both_partners"
            },
            "coverage": {
                "primary": {
                    "person": "Main Person",
                    "sum_insured_nzd": main_trauma_sum,
                    "sum_insured_formatted": format_currency(main_trauma_sum),
                    "existing_cover_nzd": main_trauma_existing,
                    "existing_cover_formatted": format_currency(main_trauma_existing),
                    "shortfall_nzd": max(0, main_trauma_sum - main_trauma_existing),
                    "shortfall_formatted": format_currency(max(0, main_trauma_sum - main_trauma_existing)),
                    "is_in_scope": main_trauma_selected
                },
                "secondary": {
                    "person": "Partner",
                    "sum_insured_nzd": partner_trauma_sum,
                    "sum_insured_formatted": format_currency(partner_trauma_sum),
                    "existing_cover_nzd": partner_trauma_existing,
                    "existing_cover_formatted": format_currency(partner_trauma_existing),
                    "shortfall_nzd": max(0, partner_trauma_sum - partner_trauma_existing),
                    "shortfall_formatted": format_currency(max(0, partner_trauma_sum - partner_trauma_existing)),
                    "is_in_scope": partner_trauma_selected
                }
            },
            "format": {
                "currency": "NZD",
                "locale": "en-NZ"
            }
        }
    else:
        result = {
            "section_id": "trauma_insurance",
            "section_type": "trauma_insurance_single",
            "scenario": "single",
            "needs_analysis": {
                "narrative": needs_analysis,
                "context": "Protection against serious illness",
                "applies_to": "individual"
            },
            "coverage": {
                "person": {
                    "sum_insured_nzd": main_trauma_sum,
                    "sum_insured_formatted": format_currency(main_trauma_sum),
                    "existing_cover_nzd": main_trauma_existing,
                    "existing_cover_formatted": format_currency(main_trauma_existing),
                    "shortfall_nzd": max(0, main_trauma_sum - main_trauma_existing),
                    "shortfall_formatted": format_currency(max(0, main_trauma_sum - main_trauma_existing)),
                    "is_in_scope": main_trauma_selected
                }
            },
            "format": {
                "currency": "NZD",
                "locale": "en-NZ"
            }
        }

    return result
