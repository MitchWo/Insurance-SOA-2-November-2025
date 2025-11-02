"""
Simplified Accidental Injury Fields Extractor
Returns clean individual field values for dynamic Zapier prompting - MVP ready with int types
"""

from typing import Dict, Any, Optional


def extract_accidental_injury_fields(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and calculate accidental injury fields from form data

    Args:
        form_data: Raw form data with field IDs

    Returns:
        Clean dictionary with individual field values for Zapier
    """

    # Helper to safely convert to boolean
    def safe_bool(value: Any, default: bool = False) -> bool:
        if value is None or value == '':
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value_lower = value.lower()
            # Handle various boolean representations
            return value_lower in ['true', 'yes', '1', 'y', 'relevant', 'needed', 'required']
        return bool(value)

    # Helper to safely get string value
    def safe_str(value: Any, default: str = '') -> str:
        if value is None:
            return default
        return str(value)

    # Extract accidental injury relevance
    main_relevant = safe_bool(form_data.get('446', False))

    # Determine if couple
    is_couple = form_data.get('is_couple', False) or form_data.get('39') == 'couple'

    # Get any notes related to accident coverage
    accident_notes = safe_str(form_data.get('accident_notes', ''))

    result = {
        # Client info
        "client_name": form_data.get('client_name', form_data.get('3', '')),
        "is_couple": is_couple,

        # Main contact fields
        "main_needs_accident_cover": main_relevant,
        "main_accident_relevant": main_relevant,

        # Summary fields
        "accident_notes": accident_notes,
    }

    # Add partner fields if couple
    if is_couple:
        partner_relevant = safe_bool(form_data.get('447', False))

        result.update({
            # Partner fields
            "partner_needs_accident_cover": partner_relevant,
            "partner_accident_relevant": partner_relevant,

            # Combined analysis
            "both_need_accident_cover": main_relevant and partner_relevant,
            "either_needs_accident_cover": main_relevant or partner_relevant,
            "total_needing_cover": sum([main_relevant, partner_relevant]),
        })

    # Add recommendation summary fields
    if is_couple:
        if main_relevant and result.get('partner_accident_relevant', False):
            result['accident_recommendation_status'] = "both_need_coverage"
        elif main_relevant:
            result['accident_recommendation_status'] = "main_only_needs_coverage"
        elif result.get('partner_accident_relevant', False):
            result['accident_recommendation_status'] = "partner_only_needs_coverage"
        else:
            result['accident_recommendation_status'] = "no_coverage_needed"
    else:
        result['accident_recommendation_status'] = "coverage_needed" if main_relevant else "no_coverage_needed"

    # Determine coverage level based on who needs it
    if is_couple and result.get('both_need_accident_cover'):
        result['accident_coverage_level'] = "family"
    elif main_relevant or result.get('partner_accident_relevant', False):
        result['accident_coverage_level'] = "individual"
    else:
        result['accident_coverage_level'] = "none"

    # Add ACC top-up recommendation flag
    # ACC top-up is typically recommended for those needing accident cover
    result['acc_topup_recommended'] = main_relevant or result.get('partner_accident_relevant', False)

    # Priority level for accident coverage
    if result['acc_topup_recommended']:
        # Accident coverage is often high priority for physical workers or high-risk activities
        result['accident_priority'] = "recommended"
    else:
        result['accident_priority'] = "not_required"

    # Coverage type indicators
    result['needs_loss_of_income'] = main_relevant or result.get('partner_accident_relevant', False)
    result['needs_lump_sum_benefit'] = main_relevant or result.get('partner_accident_relevant', False)
    result['needs_rehabilitation_costs'] = main_relevant or result.get('partner_accident_relevant', False)

    # Add section metadata

    result["section_id"] = "accidental_injury"

    result["status"] = "success"


    return result


if __name__ == "__main__":
    # Test with sample data
    import json

    # Test single person needing coverage
    sample_data_single = {
        "client_name": "John Smith",
        "is_couple": False,
        "446": "true",  # Main needs accident cover
    }

    # Test couple with both needing coverage
    sample_data_couple = {
        "client_name": "John and Jane Smith",
        "is_couple": True,
        "446": "yes",   # Main needs accident cover
        "447": "true",  # Partner needs accident cover
        "accident_notes": "Both work in construction industry"
    }

    # Test couple with only one needing coverage
    sample_data_partial = {
        "client_name": "Mike and Sarah Johnson",
        "is_couple": True,
        "446": "true",  # Main needs accident cover
        "447": "false", # Partner doesn't need accident cover
    }

    print("Single Person Test:")
    print("=" * 50)
    result = extract_accidental_injury_fields(sample_data_single)
    print(json.dumps(result, indent=2))

    print("\n\nCouple Test (Both Need):")
    print("=" * 50)
    result = extract_accidental_injury_fields(sample_data_couple)
    print(json.dumps(result, indent=2))

    print("\n\nCouple Test (One Needs):")
    print("=" * 50)
    result = extract_accidental_injury_fields(sample_data_partial)
    print(json.dumps(result, indent=2))