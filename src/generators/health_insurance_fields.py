"""
Simplified Health Insurance Fields Extractor
Returns clean individual field values for dynamic Zapier prompting - MVP ready with int types
"""

from typing import Dict, Any, Optional


def extract_health_insurance_fields(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and calculate health insurance fields from form data

    Args:
        form_data: Raw form data with field IDs

    Returns:
        Clean dictionary with individual field values for Zapier
    """

    # Helper to safely convert to float
    def safe_int(value: Any, default: int = 0) -> int:
        """Convert to integer, clamp negatives to 0"""
        if value is None or value == '':
            return default
        try:
            if isinstance(value, str):
                value = value.replace(',', '').replace('$', '')
            n = int(float(value))
            return n if n > 0 else 0
        except (ValueError, TypeError):
            return default
        try:
            if isinstance(value, str):
                value = value.replace(',', '').replace('$', '')
            return float(value)
        except (ValueError, TypeError):
            return default

    # Helper to safely convert to boolean
    def safe_bool(value: Any, default: bool = False) -> bool:
        if value is None or value == '':
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', 'yes', '1', 'y']
        return bool(value)

    # Extract main contact health insurance needs
    main_private_care_access = safe_bool(form_data.get('449', False))
    main_specialists_tests = safe_bool(form_data.get('450', False))
    main_non_pharmac = safe_bool(form_data.get('451', False))
    main_dental_optical_physio = safe_bool(form_data.get('452', False))
    main_child_coverage = safe_bool(form_data.get('454', False))
    main_base_excess = safe_int(form_data.get('453', 0))

    # Count how many coverage types are needed
    main_coverage_count = sum([
        main_private_care_access,
        main_specialists_tests,
        main_non_pharmac,
        main_dental_optical_physio,
        main_child_coverage
    ])

    # Determine coverage level based on selections
    if main_coverage_count == 0:
        main_coverage_level = "none"
    elif main_coverage_count <= 2:
        main_coverage_level = "basic"
    elif main_coverage_count <= 3:
        main_coverage_level = "moderate"
    else:
        main_coverage_level = "comprehensive"

    # Determine plan type recommendation
    if main_private_care_access and main_specialists_tests:
        if main_non_pharmac and main_dental_optical_physio:
            main_plan_type = "premium_plus"
        else:
            main_plan_type = "premium"
    elif main_specialists_tests:
        main_plan_type = "specialist"
    elif main_private_care_access:
        main_plan_type = "surgical"
    else:
        main_plan_type = "basic" if main_coverage_count > 0 else "none"

    # Determine if couple
    is_couple = form_data.get('is_couple', False) or form_data.get('39') == 'couple'

    result = {
        # Client info
        "client_name": form_data.get('client_name', form_data.get('3', '')),
        "is_couple": is_couple,

        # Main contact individual fields
        "main_private_care_access": main_private_care_access,
        "main_specialists_tests": main_specialists_tests,
        "main_non_pharmac": main_non_pharmac,
        "main_dental_optical_physio": main_dental_optical_physio,
        "main_child_coverage": main_child_coverage,
        "main_base_excess": main_base_excess,

        # Main contact calculated fields
        "main_coverage_count": main_coverage_count,
        "main_coverage_level": main_coverage_level,
        "main_plan_type": main_plan_type,
        "main_needs_health_insurance": main_coverage_count > 0,

        # Additional notes
        "health_insurance_notes": form_data.get('510', ''),
    }

    # Add partner fields if couple
    if is_couple:
        # Extract partner health insurance needs
        partner_private_care_access = safe_bool(form_data.get('456', False))
        partner_specialists_tests = safe_bool(form_data.get('457', False))
        partner_non_pharmac = safe_bool(form_data.get('458', False))
        partner_dental_optical_physio = safe_bool(form_data.get('459', False))
        partner_child_coverage = safe_bool(form_data.get('461', False))
        partner_base_excess = safe_int(form_data.get('460', 0))

        # Count partner coverage types
        partner_coverage_count = sum([
            partner_private_care_access,
            partner_specialists_tests,
            partner_non_pharmac,
            partner_dental_optical_physio,
            partner_child_coverage
        ])

        # Determine partner coverage level
        if partner_coverage_count == 0:
            partner_coverage_level = "none"
        elif partner_coverage_count <= 2:
            partner_coverage_level = "basic"
        elif partner_coverage_count <= 3:
            partner_coverage_level = "moderate"
        else:
            partner_coverage_level = "comprehensive"

        # Determine partner plan type
        if partner_private_care_access and partner_specialists_tests:
            if partner_non_pharmac and partner_dental_optical_physio:
                partner_plan_type = "premium_plus"
            else:
                partner_plan_type = "premium"
        elif partner_specialists_tests:
            partner_plan_type = "specialist"
        elif partner_private_care_access:
            partner_plan_type = "surgical"
        else:
            partner_plan_type = "basic" if partner_coverage_count > 0 else "none"

        # Add partner fields to result
        result.update({
            # Partner individual fields
            "partner_private_care_access": partner_private_care_access,
            "partner_specialists_tests": partner_specialists_tests,
            "partner_non_pharmac": partner_non_pharmac,
            "partner_dental_optical_physio": partner_dental_optical_physio,
            "partner_child_coverage": partner_child_coverage,
            "partner_base_excess": partner_base_excess,

            # Partner calculated fields
            "partner_coverage_count": partner_coverage_count,
            "partner_coverage_level": partner_coverage_level,
            "partner_plan_type": partner_plan_type,
            "partner_needs_health_insurance": partner_coverage_count > 0,

            # Combined analysis
            "combined_coverage_count": main_coverage_count + partner_coverage_count,
            "both_need_health_insurance": main_coverage_count > 0 and partner_coverage_count > 0,
            "family_plan_recommended": (main_child_coverage or partner_child_coverage) and is_couple,
        })

    # Add recommendation summary fields
    if is_couple:
        if main_coverage_count > 0 and result.get('partner_coverage_count', 0) > 0:
            result['health_insurance_recommendation_status'] = "both_need_coverage"
        elif main_coverage_count > 0:
            result['health_insurance_recommendation_status'] = "main_only_needs_coverage"
        elif result.get('partner_coverage_count', 0) > 0:
            result['health_insurance_recommendation_status'] = "partner_only_needs_coverage"
        else:
            result['health_insurance_recommendation_status'] = "no_coverage_needed"
    else:
        result['health_insurance_recommendation_status'] = "coverage_needed" if main_coverage_count > 0 else "no_coverage_needed"

    # Add specific coverage flags for easy reference
    result['needs_surgical_coverage'] = main_private_care_access or result.get('partner_private_care_access', False)
    result['needs_specialist_coverage'] = main_specialists_tests or result.get('partner_specialists_tests', False)
    result['needs_non_pharmac_coverage'] = main_non_pharmac or result.get('partner_non_pharmac', False)
    result['needs_everyday_health'] = main_dental_optical_physio or result.get('partner_dental_optical_physio', False)
    result['needs_child_coverage'] = main_child_coverage or result.get('partner_child_coverage', False)

    # Determine overall plan recommendation
    if result['needs_surgical_coverage'] and result['needs_specialist_coverage']:
        if result['needs_non_pharmac_coverage'] and result['needs_everyday_health']:
            result['recommended_plan_level'] = "premium_plus"
        else:
            result['recommended_plan_level'] = "premium"
    elif result['needs_specialist_coverage']:
        result['recommended_plan_level'] = "specialist"
    elif result['needs_surgical_coverage']:
        result['recommended_plan_level'] = "surgical"
    elif main_coverage_count > 0 or result.get('partner_coverage_count', 0) > 0:
        result['recommended_plan_level'] = "basic"
    else:
        result['recommended_plan_level'] = "none"

    # Excess recommendation
    total_excess = main_base_excess + result.get('partner_base_excess', 0)
    if total_excess == 0:
        result['excess_preference'] = "no_excess"
    elif total_excess <= 500:
        result['excess_preference'] = "low_excess"
    elif total_excess <= 1000:
        result['excess_preference'] = "moderate_excess"
    else:
        result['excess_preference'] = "high_excess"

    # Add section metadata

    result["section_id"] = "health_insurance"

    result["status"] = "success"


    return result


if __name__ == "__main__":
    # Test with sample data
    import json

    sample_data = {
        "client_name": "John Smith",
        "is_couple": True,
        "449": "true",   # Main private care access
        "450": "true",   # Main specialists tests
        "451": "false",  # Main non-pharmac
        "452": "true",   # Main dental/optical/physio
        "453": "500",    # Main base excess
        "454": "true",   # Main child coverage
        "456": "true",   # Partner private care access
        "457": "true",   # Partner specialists tests
        "458": "true",   # Partner non-pharmac
        "459": "false",  # Partner dental/optical/physio
        "460": "250",    # Partner base excess
        "461": "true",   # Partner child coverage
        "510": "Family with young children, both working professionals"
    }

    result = extract_health_insurance_fields(sample_data)
    print(json.dumps(result, indent=2))