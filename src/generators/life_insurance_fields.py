"""
Life Insurance Fields Extractor - Consolidated Version
Groups all main and partner fields into single JSON strings for Zapier
Omits zero values and maintains backward compatibility
"""

import json
from typing import Dict, Any


def extract_life_insurance_fields(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and consolidate life insurance fields for Zapier

    Returns grouped data instead of individual fields:
    - life_insurance_main_json: All main person fields as JSON string
    - life_insurance_partner_json: All partner fields as JSON string
    - needs_analysis_notes: Separate text field
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
        return f"${value:,}" if value > 0 else "$0"

    # Determine if couple
    is_couple = form_data.get('is_couple', False) or form_data.get('39') == 'couple'

    # Extract main person life insurance components
    main_components = {}

    # Only add non-zero values
    debt_repayment = safe_int(form_data.get('380', 0))
    if debt_repayment > 0:
        main_components['debt_repayment'] = debt_repayment
        main_components['debt_repayment_formatted'] = format_currency(debt_repayment)

    replacement_income = safe_int(form_data.get('381', 0))
    if replacement_income > 0:
        main_components['replacement_income'] = replacement_income
        main_components['replacement_income_formatted'] = format_currency(replacement_income)

    child_education = safe_int(form_data.get('382', 0))
    if child_education > 0:
        main_components['child_education'] = child_education
        main_components['child_education_formatted'] = format_currency(child_education)

    final_expenses = safe_int(form_data.get('383', 0))
    if final_expenses > 0:
        main_components['final_expenses'] = final_expenses
        main_components['final_expenses_formatted'] = format_currency(final_expenses)

    other_considerations = safe_int(form_data.get('384', 0))
    if other_considerations > 0:
        main_components['other_considerations'] = other_considerations
        main_components['other_considerations_formatted'] = format_currency(other_considerations)

    # Assets (offsets)
    assets_offset = safe_int(form_data.get('386', 0))
    if assets_offset > 0:
        main_components['assets_offset'] = assets_offset
        main_components['assets_offset_formatted'] = format_currency(assets_offset)

    kiwisaver_offset = safe_int(form_data.get('388', 0))
    if kiwisaver_offset > 0:
        main_components['kiwisaver_offset'] = kiwisaver_offset
        main_components['kiwisaver_offset_formatted'] = format_currency(kiwisaver_offset)

    # Total cover needed
    total_cover = safe_int(form_data.get('389', 0))
    if total_cover > 0:
        main_components['total_cover_needed'] = total_cover
        main_components['total_cover_formatted'] = format_currency(total_cover)

    # Calculate totals
    total_needs = sum([
        main_components.get('debt_repayment', 0),
        main_components.get('replacement_income', 0),
        main_components.get('child_education', 0),
        main_components.get('final_expenses', 0),
        main_components.get('other_considerations', 0)
    ])

    total_offsets = sum([
        main_components.get('assets_offset', 0),
        main_components.get('kiwisaver_offset', 0)
    ])

    net_coverage = max(0, total_needs - total_offsets)

    if total_needs > 0:
        main_components['total_needs'] = total_needs
        main_components['total_needs_formatted'] = format_currency(total_needs)

    if total_offsets > 0:
        main_components['total_offsets'] = total_offsets
        main_components['total_offsets_formatted'] = format_currency(total_offsets)

    if net_coverage > 0:
        main_components['net_coverage_required'] = net_coverage
        main_components['net_coverage_formatted'] = format_currency(net_coverage)

    # Add summary flag
    if main_components:
        main_components['needs_life_insurance'] = True

    # Extract partner components if couple
    partner_components = {}

    if is_couple:
        partner_debt = safe_int(form_data.get('391', 0))
        if partner_debt > 0:
            partner_components['debt_repayment'] = partner_debt
            partner_components['debt_repayment_formatted'] = format_currency(partner_debt)

        partner_income = safe_int(form_data.get('392', 0))
        if partner_income > 0:
            partner_components['replacement_income'] = partner_income
            partner_components['replacement_income_formatted'] = format_currency(partner_income)

        partner_education = safe_int(form_data.get('393', 0))
        if partner_education > 0:
            partner_components['child_education'] = partner_education
            partner_components['child_education_formatted'] = format_currency(partner_education)

        partner_final = safe_int(form_data.get('394', 0))
        if partner_final > 0:
            partner_components['final_expenses'] = partner_final
            partner_components['final_expenses_formatted'] = format_currency(partner_final)

        partner_other = safe_int(form_data.get('395', 0))
        if partner_other > 0:
            partner_components['other_considerations'] = partner_other
            partner_components['other_considerations_formatted'] = format_currency(partner_other)

        partner_assets = safe_int(form_data.get('397', 0))
        if partner_assets > 0:
            partner_components['assets_offset'] = partner_assets
            partner_components['assets_offset_formatted'] = format_currency(partner_assets)

        partner_kiwisaver = safe_int(form_data.get('399', 0))
        if partner_kiwisaver > 0:
            partner_components['kiwisaver_offset'] = partner_kiwisaver
            partner_components['kiwisaver_offset_formatted'] = format_currency(partner_kiwisaver)

        partner_total = safe_int(form_data.get('400', 0))
        if partner_total > 0:
            partner_components['total_cover_needed'] = partner_total
            partner_components['total_cover_formatted'] = format_currency(partner_total)

        # Calculate partner totals
        partner_total_needs = sum([
            partner_components.get('debt_repayment', 0),
            partner_components.get('replacement_income', 0),
            partner_components.get('child_education', 0),
            partner_components.get('final_expenses', 0),
            partner_components.get('other_considerations', 0)
        ])

        partner_total_offsets = sum([
            partner_components.get('assets_offset', 0),
            partner_components.get('kiwisaver_offset', 0)
        ])

        partner_net = max(0, partner_total_needs - partner_total_offsets)

        if partner_total_needs > 0:
            partner_components['total_needs'] = partner_total_needs
            partner_components['total_needs_formatted'] = format_currency(partner_total_needs)

        if partner_total_offsets > 0:
            partner_components['total_offsets'] = partner_total_offsets
            partner_components['total_offsets_formatted'] = format_currency(partner_total_offsets)

        if partner_net > 0:
            partner_components['net_coverage_required'] = partner_net
            partner_components['net_coverage_formatted'] = format_currency(partner_net)

        if partner_components:
            partner_components['needs_life_insurance'] = True

    # Extract needs analysis notes
    needs_notes = form_data.get('504', '').strip()

    # Build consolidated response
    result = {
        # Client info
        "client_name": form_data.get('client_name', form_data.get('3', '')),
        "is_couple": is_couple,

        # Consolidated JSON fields for Zapier (single data points)
        "life_insurance_main_json": json.dumps(main_components) if main_components else "{}",
        "life_insurance_partner_json": json.dumps(partner_components) if partner_components else "{}",

        # Separate needs analysis note
        "needs_analysis_notes": needs_notes,

        # Summary flags for logic
        "main_needs_insurance": len(main_components) > 0,
        "partner_needs_insurance": len(partner_components) > 0,

        # Overall recommendation status
        "recommendation_status": "no_coverage_needed",

        # Section metadata
        "section_id": "life_insurance",
        "status": "success"
    }

    # Determine recommendation status
    if main_components and partner_components:
        result['recommendation_status'] = "both_need_coverage"
    elif main_components:
        result['recommendation_status'] = "main_only_needs_coverage"
    elif partner_components:
        result['recommendation_status'] = "partner_only_needs_coverage"

    # Add formatted text summaries for easy reading
    def create_summary_text(components: Dict, label: str) -> str:
        """Create readable text summary"""
        if not components:
            return f"{label}: No life insurance needed"

        lines = [f"{label} Life Insurance Needs:"]

        if 'debt_repayment' in components:
            lines.append(f"  Debt Repayment: {components['debt_repayment_formatted']}")
        if 'replacement_income' in components:
            lines.append(f"  Income Replacement: {components['replacement_income_formatted']}")
        if 'child_education' in components:
            lines.append(f"  Child Education: {components['child_education_formatted']}")
        if 'final_expenses' in components:
            lines.append(f"  Final Expenses: {components['final_expenses_formatted']}")
        if 'other_considerations' in components:
            lines.append(f"  Other: {components['other_considerations_formatted']}")

        if 'total_needs_formatted' in components:
            lines.append(f"  Total Needs: {components['total_needs_formatted']}")

        if 'assets_offset' in components or 'kiwisaver_offset' in components:
            lines.append("  Less Offsets:")
            if 'assets_offset' in components:
                lines.append(f"    Assets: {components['assets_offset_formatted']}")
            if 'kiwisaver_offset' in components:
                lines.append(f"    KiwiSaver: {components['kiwisaver_offset_formatted']}")

        if 'net_coverage_formatted' in components:
            lines.append(f"  Net Coverage Required: {components['net_coverage_formatted']}")

        return "\n".join(lines)

    result['main_summary_text'] = create_summary_text(main_components, "Main Person")
    result['partner_summary_text'] = create_summary_text(partner_components, "Partner") if is_couple else ""

    return result
