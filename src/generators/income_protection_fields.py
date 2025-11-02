"""
Simplified Income Protection Fields Extractor
Returns clean individual field values for dynamic Zapier prompting - MVP ready with int types
"""

from typing import Dict, Any, Optional


def extract_income_protection_fields(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and calculate income protection fields from form data

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

    # Helper to safely convert to int
    def safe_int(value: Any, default: int = 0) -> int:
        if value is None or value == '':
            return default
        try:
            if isinstance(value, str):
                value = value.replace(',', '')
            return int(float(value))
        except (ValueError, TypeError):
            return default

    # Extract main contact income protection needs
    main_monthly_mortgage = safe_int(form_data.get('420', 0))
    main_living_expenses = safe_int(form_data.get('421', 0))
    main_max_insurable_income = safe_int(form_data.get('422', 0))
    main_income_type = form_data.get('423', '')
    main_loe_mrc_type = form_data.get('424', '')
    main_acc_offsets = safe_int(form_data.get('425', 0))
    main_savings = safe_int(form_data.get('427', 0))
    main_leave_entitlements_dollars = safe_int(form_data.get('428', 0))
    main_leave_entitlements_weeks = safe_int(form_data.get('429', 0))
    main_wait_period_weeks = safe_int(form_data.get('430', 0))
    main_claim_period_years = safe_int(form_data.get('431', 0))

    # Calculate main monthly needs
    main_monthly_needs = main_monthly_mortgage + main_living_expenses

    # Calculate main annual needs
    main_annual_needs = main_monthly_needs * 12

    # Calculate recommended coverage (typically 75% of income or actual needs, whichever is lower)
    main_recommended_coverage = min(main_annual_needs, main_max_insurable_income * 0.75) if main_max_insurable_income > 0 else main_annual_needs

    # Calculate monthly benefit amount
    main_monthly_benefit = main_recommended_coverage / 12 if main_recommended_coverage > 0 else 0

    # Determine if couple
    is_couple = form_data.get('is_couple', False) or form_data.get('39') == 'couple'

    result = {
        # Client info
        "client_name": form_data.get('client_name', form_data.get('3', '')),
        "is_couple": is_couple,

        # Main contact individual fields
        "main_monthly_mortgage": main_monthly_mortgage,
        "main_living_expenses": main_living_expenses,
        "main_max_insurable_income": main_max_insurable_income,
        "main_income_type": main_income_type,
        "main_loe_mrc_type": main_loe_mrc_type,
        "main_acc_offsets": main_acc_offsets,
        "main_savings": main_savings,
        "main_leave_entitlements_dollars": main_leave_entitlements_dollars,
        "main_leave_entitlements_weeks": main_leave_entitlements_weeks,
        "main_wait_period_weeks": main_wait_period_weeks,
        "main_claim_period_years": main_claim_period_years,

        # Main contact calculated fields
        "main_monthly_needs": main_monthly_needs,
        "main_annual_needs": main_annual_needs,
        "main_recommended_coverage": main_recommended_coverage,
        "main_monthly_benefit": main_monthly_benefit,
        "main_needs_income_protection": main_monthly_needs > 0,

        # Additional notes
        "income_protection_notes": form_data.get('508', ''),
    }

    # Add partner fields if couple
    if is_couple:
        # Extract partner income protection needs
        partner_monthly_mortgage = safe_int(form_data.get('433', 0))
        partner_living_expenses = safe_int(form_data.get('434', 0))
        partner_max_insurable_income = safe_int(form_data.get('435', 0))
        partner_income_type = form_data.get('436', '')
        partner_loe_mrc_type = form_data.get('437', '')
        partner_acc_offsets = safe_int(form_data.get('438', 0))
        partner_savings = safe_int(form_data.get('440', 0))
        partner_leave_entitlements_dollars = safe_int(form_data.get('441', 0))
        partner_leave_entitlements_weeks = safe_int(form_data.get('442', 0))
        partner_wait_period_weeks = safe_int(form_data.get('443', 0))
        partner_claim_period_years = safe_int(form_data.get('444', 0))

        # Calculate partner monthly needs
        partner_monthly_needs = partner_monthly_mortgage + partner_living_expenses

        # Calculate partner annual needs
        partner_annual_needs = partner_monthly_needs * 12

        # Calculate recommended coverage for partner
        partner_recommended_coverage = min(partner_annual_needs, partner_max_insurable_income * 0.75) if partner_max_insurable_income > 0 else partner_annual_needs

        # Calculate monthly benefit amount for partner
        partner_monthly_benefit = partner_recommended_coverage / 12 if partner_recommended_coverage > 0 else 0

        # Add partner fields to result
        result.update({
            # Partner individual fields
            "partner_monthly_mortgage": partner_monthly_mortgage,
            "partner_living_expenses": partner_living_expenses,
            "partner_max_insurable_income": partner_max_insurable_income,
            "partner_income_type": partner_income_type,
            "partner_loe_mrc_type": partner_loe_mrc_type,
            "partner_acc_offsets": partner_acc_offsets,
            "partner_savings": partner_savings,
            "partner_leave_entitlements_dollars": partner_leave_entitlements_dollars,
            "partner_leave_entitlements_weeks": partner_leave_entitlements_weeks,
            "partner_wait_period_weeks": partner_wait_period_weeks,
            "partner_claim_period_years": partner_claim_period_years,

            # Partner calculated fields
            "partner_monthly_needs": partner_monthly_needs,
            "partner_annual_needs": partner_annual_needs,
            "partner_recommended_coverage": partner_recommended_coverage,
            "partner_monthly_benefit": partner_monthly_benefit,
            "partner_needs_income_protection": partner_monthly_needs > 0,

            # Combined totals
            "combined_monthly_needs": main_monthly_needs + partner_monthly_needs,
            "combined_annual_needs": main_annual_needs + partner_annual_needs,
            "combined_monthly_benefit": main_monthly_benefit + partner_monthly_benefit,
            "both_need_income_protection": main_monthly_needs > 0 and partner_monthly_needs > 0,
        })

    # Add recommendation summary fields
    if is_couple:
        if main_monthly_needs > 0 and result.get('partner_monthly_needs', 0) > 0:
            result['income_protection_recommendation_status'] = "both_need_coverage"
        elif main_monthly_needs > 0:
            result['income_protection_recommendation_status'] = "main_only_needs_coverage"
        elif result.get('partner_monthly_needs', 0) > 0:
            result['income_protection_recommendation_status'] = "partner_only_needs_coverage"
        else:
            result['income_protection_recommendation_status'] = "no_coverage_needed"
    else:
        result['income_protection_recommendation_status'] = "coverage_needed" if main_monthly_needs > 0 else "no_coverage_needed"

    # Add coverage level indicator
    total_monthly_benefit = main_monthly_benefit + result.get('partner_monthly_benefit', 0)
    if total_monthly_benefit == 0:
        result['income_protection_coverage_level'] = "none"
    elif total_monthly_benefit < 5000:
        result['income_protection_coverage_level'] = "basic"
    elif total_monthly_benefit < 10000:
        result['income_protection_coverage_level'] = "moderate"
    else:
        result['income_protection_coverage_level'] = "comprehensive"

    # Add wait period analysis
    if main_wait_period_weeks > 0:
        if main_wait_period_weeks <= 4:
            result['main_wait_period_type'] = "short"
        elif main_wait_period_weeks <= 13:
            result['main_wait_period_type'] = "medium"
        else:
            result['main_wait_period_type'] = "long"
    else:
        result['main_wait_period_type'] = "not_specified"

    # Add claim period analysis
    if main_claim_period_years > 0:
        if main_claim_period_years <= 2:
            result['main_claim_period_type'] = "short_term"
        elif main_claim_period_years <= 5:
            result['main_claim_period_type'] = "medium_term"
        else:
            result['main_claim_period_type'] = "to_age_65_or_longer"
    else:
        result['main_claim_period_type'] = "not_specified"

    # Add flags for coverage components
    result['has_mortgage_coverage'] = main_monthly_mortgage > 0
    result['has_living_expenses_coverage'] = main_living_expenses > 0
    result['has_acc_offsets'] = main_acc_offsets > 0
    result['has_leave_entitlements'] = main_leave_entitlements_dollars > 0 or main_leave_entitlements_weeks > 0
    result['has_savings_buffer'] = main_savings > 0

    # Add section metadata

    result["section_id"] = "income_protection"

    result["status"] = "success"


    return result


if __name__ == "__main__":
    # Test with sample data
    import json

    sample_data = {
        "client_name": "John Smith",
        "is_couple": True,
        "420": "3000",   # Main monthly mortgage
        "421": "2000",   # Main living expenses
        "422": "100000", # Main max insurable income
        "423": "salary", # Main income type
        "424": "LOE",    # Main LOE/MRC type
        "425": "1000",   # Main ACC offsets
        "427": "10000",  # Main savings
        "428": "5000",   # Main leave entitlements dollars
        "429": "4",      # Main leave entitlements weeks
        "430": "13",     # Main wait period weeks
        "431": "5",      # Main claim period years
        "433": "2500",   # Partner monthly mortgage
        "434": "1800",   # Partner living expenses
        "435": "80000",  # Partner max income
        "436": "salary", # Partner income type
        "437": "MRC",    # Partner LOE/MRC type
        "438": "800",    # Partner ACC offsets
        "440": "8000",   # Partner savings
        "441": "4000",   # Partner leave entitlements dollars
        "442": "3",      # Partner leave entitlements weeks
        "443": "26",     # Partner wait period weeks
        "444": "2",      # Partner claim period years
        "508": "Both working professionals with mortgage"
    }

    result = extract_income_protection_fields(sample_data)
    print(json.dumps(result, indent=2))