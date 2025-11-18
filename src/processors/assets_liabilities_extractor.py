"""
Assets and Liabilities Extractor
Extracts and formats all assets and liabilities as simple text tables for Zapier
Omits zero/empty values and provides comprehensive totals
"""

import json
from typing import Dict, Any, List


def safe_int(value: Any, default: int = 0) -> int:
    """Convert to integer, handling currency strings"""
    if not value or value == "":
        return default
    if isinstance(value, (int, float)):
        return max(0, int(value))
    cleaned = str(value).replace('$', '').replace(',', '').strip()
    try:
        return max(0, int(float(cleaned)))
    except:
        return default


def get_first_valid_value(data: Dict[str, Any], field_list: list, default: Any = 0) -> Any:
    """Get the first non-empty value from a list of field keys"""
    for field in field_list:
        value = data.get(field, '')
        if value and str(value).strip() != '':
            return value
    return default


def format_currency(value: int) -> str:
    """Format as currency"""
    return f"${value:,}"


def extract_assets_liabilities(combined_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and format assets and liabilities as simple JSON arrays and text tables

    Returns a dictionary with:
    - assets_json: JSON string array of asset objects
    - liabilities_json: JSON string array of liability objects
    - assets_text: Formatted text table of assets
    - liabilities_text: Formatted text table of liabilities
    - summary_text: Summary with totals
    """

    # Collect all assets
    assets = []

    # Owner occupied property - use helper to get first valid value
    house_value = safe_int(get_first_valid_value(combined_data, ['16'], 0))
    if house_value > 0:
        assets.append({
            "name": "Owner Occupied",
            "value": house_value,
            "formatted": format_currency(house_value)
        })

    # Investment properties
    investment_value = safe_int(combined_data.get('468', 0))
    if investment_value > 0:
        assets.append({
            "name": "Investment Properties",
            "value": investment_value,
            "formatted": format_currency(investment_value)
        })

    # General assets - Handle both documented patterns and edge cases

    # Special case: Field 33 (not in original spec but contains data)
    # This appears to be paired with field 26 based on Ryan's data
    field_33_name = combined_data.get('33', '').strip()
    field_26_value = safe_int(combined_data.get('26', 0))

    # Check if field 22 is empty but field 26 has value (orphan value scenario)
    field_22_name = combined_data.get('22', '').strip()

    if field_33_name and field_26_value > 0 and not field_22_name:
        # Field 33 is using the orphan value from field 26
        assets.append({
            "name": field_33_name,
            "value": field_26_value,
            "formatted": format_currency(field_26_value)
        })
    elif field_22_name and field_26_value > 0:
        # Normal Asset 1 mapping (field 22/26)
        assets.append({
            "name": field_22_name,
            "value": field_26_value,
            "formatted": format_currency(field_26_value)
        })

    # Continue with remaining documented asset pairs
    asset_pairs = [
        ('19', '36'),   # Asset 2: Managed Funds - Foodstuffs (confirmed in data)
        ('35', '34'),   # Asset 3
        ('45', '46'),   # Asset 4
        ('47', '287'),  # Asset 5
        ('186', '48'),  # Asset 6
        ('198', '199'), # Asset 7
        ('189', '188'), # Asset 8
        ('192', '193'), # Asset 9
        ('195', '196'), # Asset 10
        ('201', '202'), # Asset 11
        ('204', '205'), # Asset 12
        ('207', '20'),  # Asset 13
        ('210', '211'), # Asset 14
        ('213', '214')  # Asset 15
    ]

    for name_field, value_field in asset_pairs:
        name = combined_data.get(name_field, '').strip()
        value = safe_int(combined_data.get(value_field, 0))

        if name and value > 0:
            assets.append({
                "name": name,
                "value": value,
                "formatted": format_currency(value)
            })

    # KiwiSaver accounts
    kiwisaver_accounts = [
        ('60', '62', 'Main'),      # Main provider, balance
        ('63', '65', 'Partner'),   # Partner provider, balance
        ('215', '217', 'Additional') # Additional provider, balance
    ]

    for provider_field, balance_field, label in kiwisaver_accounts:
        provider = combined_data.get(provider_field, '').strip()
        balance = safe_int(combined_data.get(balance_field, 0))

        if balance > 0:
            name = f"KiwiSaver - {provider}" if provider else f"KiwiSaver ({label})"
            assets.append({
                "name": name,
                "value": balance,
                "formatted": format_currency(balance)
            })

    # Collect all liabilities
    liabilities = []

    # Home mortgage
    mortgage = safe_int(combined_data.get('15', 0))
    if mortgage > 0:
        liabilities.append({
            "name": "Home Mortgage",
            "value": mortgage,
            "formatted": format_currency(mortgage)
        })

    # Investment property debt
    investment_debt = safe_int(combined_data.get('469', 0))
    if investment_debt > 0:
        liabilities.append({
            "name": "Investment Property Mortgages",
            "value": investment_debt,
            "formatted": format_currency(investment_debt)
        })

    # General liabilities (1-5)
    liability_pairs = [
        ('71', '72'), ('73', '74'), ('75', '76'), ('77', '78'), ('88', '89')
    ]

    for name_field, value_field in liability_pairs:
        name = combined_data.get(name_field, '').strip()
        value = safe_int(combined_data.get(value_field, 0))

        if name and value > 0:
            liabilities.append({
                "name": name,
                "value": value,
                "formatted": format_currency(value)
            })

    # Calculate totals
    total_assets = sum(a['value'] for a in assets)
    total_liabilities = sum(l['value'] for l in liabilities)
    net_worth = total_assets - total_liabilities

    # Get form-provided totals for validation (if available)
    form_asset_total = safe_int(combined_data.get('466', 0))  # Asset Total field

    # Create simple text tables
    def create_text_table(items: List[Dict], title: str, total: int) -> str:
        """Create a simple text table"""
        if not items:
            return f"No {title.lower()} recorded"

        lines = []
        lines.append(title)
        lines.append("-" * 50)

        for item in items:
            lines.append(f"{item['name']:<35} {item['formatted']:>12}")

        lines.append("-" * 50)
        lines.append(f"{'Total ' + title:<35} {format_currency(total):>12}")

        return "\n".join(lines)

    assets_text = create_text_table(assets, "Assets", total_assets)
    liabilities_text = create_text_table(liabilities, "Liabilities", total_liabilities)

    # Create summary text
    summary_text = f"""Financial Summary
--------------------------------------------------
Total Assets:                   {format_currency(total_assets):>15}
Total Liabilities:              {format_currency(total_liabilities):>15}
--------------------------------------------------
Net Worth:                      {format_currency(net_worth):>15}"""

    # Add validation note if form total differs from calculated total
    validation_note = ""
    if form_asset_total > 0 and form_asset_total != total_assets:
        validation_note = f"Note: Form asset total (${form_asset_total:,}) differs from calculated total (${total_assets:,})"

    # Return structured data
    return {
        "section_id": "assets_liabilities",
        "section_type": "financial_position",

        # JSON arrays as strings (single fields for Zapier)
        "assets_json": json.dumps(assets),
        "liabilities_json": json.dumps(liabilities),

        # Simple text tables (single fields for Zapier)
        "assets_text": assets_text,
        "liabilities_text": liabilities_text,
        "summary_text": summary_text,

        # Numeric values for calculations
        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "net_worth": net_worth,
        "asset_count": len(assets),
        "liability_count": len(liabilities),

        # Validation data
        "form_asset_total": form_asset_total,
        "validation_note": validation_note,

        "status": "success"
    }
