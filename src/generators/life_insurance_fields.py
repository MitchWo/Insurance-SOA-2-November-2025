"""
Simplified Life Insurance Fields Extractor
Returns clean individual field values for dynamic Zapier prompting
"""

from typing import Dict, Any, Optional


def extract_life_insurance_fields(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and calculate life insurance fields from form data

    Args:
        form_data: Raw form data with field IDs

    Returns:
        Clean dictionary with individual field values for Zapier
    """

    # Helper to safely convert to float
    def safe_float(value: Any, default: float = 0.0) -> float:
        if value is None or value == '':
            return default
        try:
            if isinstance(value, str):
                value = value.replace(',', '').replace('$', '')
            return float(value)
        except (ValueError, TypeError):
            return default

    # Extract main contact needs
    main_debt_repayment = safe_float(form_data.get('380', 0))
    main_replacement_income = safe_float(form_data.get('381', 0))
    main_child_education = safe_float(form_data.get('382', 0))
    main_final_expenses = safe_float(form_data.get('383', 0))
    main_other_considerations = safe_float(form_data.get('384', 0))

    # Extract main contact offsets
    main_assets = safe_float(form_data.get('386', 0))
    main_kiwisaver = safe_float(form_data.get('388', 0))

    # Calculate main totals
    main_total_needs = (main_debt_repayment + main_replacement_income +
                       main_child_education + main_final_expenses +
                       main_other_considerations)
    main_total_offsets = main_assets + main_kiwisaver
    main_net_coverage = max(0, main_total_needs - main_total_offsets)

    # Determine if couple
    is_couple = form_data.get('is_couple', False) or form_data.get('39') == 'couple'

    result = {
        # Client info
        "client_name": form_data.get('client_name', form_data.get('3', '')),
        "is_couple": is_couple,

        # Main contact individual fields
        "main_debt_repayment": main_debt_repayment,
        "main_replacement_income": main_replacement_income,
        "main_child_education": main_child_education,
        "main_final_expenses": main_final_expenses,
        "main_other_considerations": main_other_considerations,
        "main_assets": main_assets,
        "main_kiwisaver": main_kiwisaver,

        # Main contact calculated fields
        "main_total_needs": main_total_needs,
        "main_total_offsets": main_total_offsets,
        "main_net_coverage": main_net_coverage,
        "main_needs_insurance": main_net_coverage > 0,

        # Additional notes
        "needs_analysis_notes": form_data.get('504', ''),
    }

    # Add partner fields if couple
    if is_couple:
        # Extract partner needs
        partner_debt_repayment = safe_float(form_data.get('391', 0))
        partner_replacement_income = safe_float(form_data.get('392', 0))
        partner_child_education = safe_float(form_data.get('393', 0))
        partner_final_expenses = safe_float(form_data.get('394', 0))
        partner_other_considerations = safe_float(form_data.get('395', 0))

        # Extract partner offsets
        partner_assets = safe_float(form_data.get('397', 0))
        partner_kiwisaver = safe_float(form_data.get('399', 0))

        # Calculate partner totals
        partner_total_needs = (partner_debt_repayment + partner_replacement_income +
                              partner_child_education + partner_final_expenses +
                              partner_other_considerations)
        partner_total_offsets = partner_assets + partner_kiwisaver
        partner_net_coverage = max(0, partner_total_needs - partner_total_offsets)

        # Add partner fields to result
        result.update({
            # Partner individual fields
            "partner_debt_repayment": partner_debt_repayment,
            "partner_replacement_income": partner_replacement_income,
            "partner_child_education": partner_child_education,
            "partner_final_expenses": partner_final_expenses,
            "partner_other_considerations": partner_other_considerations,
            "partner_assets": partner_assets,
            "partner_kiwisaver": partner_kiwisaver,

            # Partner calculated fields
            "partner_total_needs": partner_total_needs,
            "partner_total_offsets": partner_total_offsets,
            "partner_net_coverage": partner_net_coverage,
            "partner_needs_insurance": partner_net_coverage > 0,

            # Combined totals
            "combined_net_coverage": main_net_coverage + partner_net_coverage,
            "both_need_insurance": main_net_coverage > 0 and partner_net_coverage > 0,
        })

    # Add recommendation summary fields
    if is_couple:
        if main_net_coverage > 0 and result.get('partner_net_coverage', 0) > 0:
            result['recommendation_status'] = "both_need_coverage"
        elif main_net_coverage > 0:
            result['recommendation_status'] = "main_only_needs_coverage"
        elif result.get('partner_net_coverage', 0) > 0:
            result['recommendation_status'] = "partner_only_needs_coverage"
        else:
            result['recommendation_status'] = "no_coverage_needed"
    else:
        result['recommendation_status'] = "coverage_needed" if main_net_coverage > 0 else "no_coverage_needed"

    # Add coverage level indicator
    total_coverage = main_net_coverage + result.get('partner_net_coverage', 0)
    if total_coverage == 0:
        result['coverage_level'] = "none"
    elif total_coverage < 250000:
        result['coverage_level'] = "basic"
    elif total_coverage < 750000:
        result['coverage_level'] = "moderate"
    else:
        result['coverage_level'] = "comprehensive"

    return result


if __name__ == "__main__":
    # Test with sample data
    import json

    sample_data = {
        "client_name": "John Smith",
        "is_couple": True,
        "380": "500000",  # Main debt
        "381": "300000",  # Main income
        "382": "100000",  # Main education
        "383": "20000",   # Main final
        "384": "50000",   # Main other
        "386": "150000",  # Main assets
        "388": "80000",   # Main KiwiSaver
        "391": "500000",  # Partner debt
        "392": "200000",  # Partner income
        "393": "100000",  # Partner education
        "394": "20000",   # Partner final
        "395": "30000",   # Partner other
        "397": "100000",  # Partner assets
        "399": "60000",   # Partner KiwiSaver
        "504": "Family with young children"
    }

    result = extract_life_insurance_fields(sample_data)
    print(json.dumps(result, indent=2))