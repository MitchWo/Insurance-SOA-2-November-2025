"""
Simplified Trauma Insurance Fields Extractor
Returns clean individual field values for dynamic Zapier prompting - MVP ready with int types
"""

from typing import Dict, Any, Optional


def extract_trauma_insurance_fields(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and calculate trauma insurance fields from form data

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

    # Extract main contact trauma needs
    main_replacement_income = safe_int(form_data.get('402', 0))
    main_replacement_expenses = safe_int(form_data.get('486', 0))
    main_debt_repayment = safe_int(form_data.get('403', 0))
    main_medical_bills = safe_int(form_data.get('404', 0))
    main_childcare_assistance = safe_int(form_data.get('405', 0))
    main_buyback_option = safe_int(form_data.get('406', 0))
    main_tpd_addon = safe_int(form_data.get('407', 0))
    main_additional_child_trauma = safe_int(form_data.get('408', 0))

    # Calculate main total (or use provided total)
    main_total_provided = safe_int(form_data.get('409', 0))
    main_total_calculated = (main_replacement_income + main_replacement_expenses +
                            main_debt_repayment + main_medical_bills +
                            main_childcare_assistance + main_buyback_option +
                            main_tpd_addon + main_additional_child_trauma)

    # Use provided total if available, otherwise calculated
    main_total = main_total_provided if main_total_provided > 0 else main_total_calculated

    # Determine if couple
    is_couple = form_data.get('is_couple', False) or form_data.get('39') == 'couple'

    result = {
        # Client info
        "client_name": form_data.get('client_name', form_data.get('3', '')),
        "is_couple": is_couple,

        # Main contact individual fields
        "main_replacement_income": main_replacement_income,
        "main_replacement_expenses": main_replacement_expenses,
        "main_debt_repayment": main_debt_repayment,
        "main_medical_bills": main_medical_bills,
        "main_childcare_assistance": main_childcare_assistance,
        "main_buyback_option": main_buyback_option,
        "main_tpd_addon": main_tpd_addon,
        "main_additional_child_trauma": main_additional_child_trauma,

        # Main contact calculated fields
        "main_total_trauma": main_total,
        "main_needs_trauma": main_total > 0,

        # Additional notes
        "trauma_notes": form_data.get('506', ''),
    }

    # Add partner fields if couple
    if is_couple:
        # Extract partner trauma needs
        partner_replacement_income = safe_int(form_data.get('411', 0))
        partner_replacement_expenses = safe_int(form_data.get('487', 0))
        partner_debt_repayment = safe_int(form_data.get('412', 0))
        partner_medical_bills = safe_int(form_data.get('413', 0))
        partner_childcare_assistance = safe_int(form_data.get('414', 0))
        partner_buyback_option = safe_int(form_data.get('415', 0))
        partner_tpd_addon = safe_int(form_data.get('416', 0))
        partner_additional_child_trauma = safe_int(form_data.get('417', 0))

        # Calculate partner total (or use provided total)
        partner_total_provided = safe_int(form_data.get('418', 0))
        partner_total_calculated = (partner_replacement_income + partner_replacement_expenses +
                                   partner_debt_repayment + partner_medical_bills +
                                   partner_childcare_assistance + partner_buyback_option +
                                   partner_tpd_addon + partner_additional_child_trauma)

        # Use provided total if available, otherwise calculated
        partner_total = partner_total_provided if partner_total_provided > 0 else partner_total_calculated

        # Add partner fields to result
        result.update({
            # Partner individual fields
            "partner_replacement_income": partner_replacement_income,
            "partner_replacement_expenses": partner_replacement_expenses,
            "partner_debt_repayment": partner_debt_repayment,
            "partner_medical_bills": partner_medical_bills,
            "partner_childcare_assistance": partner_childcare_assistance,
            "partner_buyback_option": partner_buyback_option,
            "partner_tpd_addon": partner_tpd_addon,
            "partner_additional_child_trauma": partner_additional_child_trauma,

            # Partner calculated fields
            "partner_total_trauma": partner_total,
            "partner_needs_trauma": partner_total > 0,

            # Combined totals
            "combined_trauma_coverage": main_total + partner_total,
            "both_need_trauma": main_total > 0 and partner_total > 0,
        })

    # Add recommendation summary fields
    if is_couple:
        if main_total > 0 and result.get('partner_total_trauma', 0) > 0:
            result['trauma_recommendation_status'] = "both_need_coverage"
        elif main_total > 0:
            result['trauma_recommendation_status'] = "main_only_needs_coverage"
        elif result.get('partner_total_trauma', 0) > 0:
            result['trauma_recommendation_status'] = "partner_only_needs_coverage"
        else:
            result['trauma_recommendation_status'] = "no_coverage_needed"
    else:
        result['trauma_recommendation_status'] = "coverage_needed" if main_total > 0 else "no_coverage_needed"

    # Add coverage level indicator for trauma
    total_coverage = main_total + result.get('partner_total_trauma', 0)
    if total_coverage == 0:
        result['trauma_coverage_level'] = "none"
    elif total_coverage < 100000:
        result['trauma_coverage_level'] = "basic"
    elif total_coverage < 300000:
        result['trauma_coverage_level'] = "moderate"
    else:
        result['trauma_coverage_level'] = "comprehensive"

    # Add breakdown flags for what's included
    result['includes_income_support'] = (main_replacement_income > 0 or
                                         main_replacement_expenses > 0)
    result['includes_medical_costs'] = main_medical_bills > 0
    result['includes_childcare'] = main_childcare_assistance > 0
    result['includes_tpd_addon'] = main_tpd_addon > 0
    result['includes_child_trauma'] = main_additional_child_trauma > 0

    # Add section metadata

    result["section_id"] = "trauma_insurance"

    result["status"] = "success"


    return result


if __name__ == "__main__":
    # Test with sample data
    import json

    sample_data = {
        "client_name": "John Smith",
        "is_couple": True,
        "402": "50000",   # Main replacement income
        "486": "30000",   # Main replacement expenses
        "403": "100000",  # Main debt repayment
        "404": "50000",   # Main medical bills
        "405": "20000",   # Main childcare
        "406": "10000",   # Main buyback
        "407": "5000",    # Main TPD addon
        "408": "15000",   # Main child trauma
        "409": "280000",  # Main total
        "411": "40000",   # Partner replacement income
        "487": "25000",   # Partner replacement expenses
        "412": "100000",  # Partner debt repayment
        "413": "50000",   # Partner medical bills
        "414": "20000",   # Partner childcare
        "415": "10000",   # Partner buyback
        "416": "5000",    # Partner TPD addon
        "417": "15000",   # Partner child trauma
        "418": "265000",  # Partner total
        "506": "Family with young children, both working"
    }

    result = extract_trauma_insurance_fields(sample_data)
    print(json.dumps(result, indent=2))