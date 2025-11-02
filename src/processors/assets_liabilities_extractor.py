"""
Assets and Liabilities Extractor
Extracts assets and liabilities in simple table format for Zapier consumption
Direct data extraction without prose generation
"""

from typing import Dict, Any, List, Optional


def extract_assets_liabilities(combined_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract assets and liabilities in table format for Zapier.
    Simple data extraction without prose generation.

    Args:
        combined_data: Combined fact find and automation form data

    Returns:
        Dictionary with assets and liabilities in table format
    """

    def safe_get(data: dict, field: str, default: Any = "") -> Any:
        """Safely get a field value with a default"""
        return data.get(field, default) if data else default

    def parse_currency(value: Any) -> float:
        """Convert string currency to number, return 0 if empty"""
        if not value:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        # Remove $, commas, and convert to float
        cleaned = str(value).replace('$', '').replace(',', '').strip()
        try:
            return float(cleaned)
        except:
            return 0.0

    # Property assets - try multiple field variations
    property_assets = {
        "current_house_value": parse_currency(safe_get(combined_data, "15", safe_get(combined_data, "468", 0))),
        "current_house_address": safe_get(combined_data, "16", safe_get(combined_data, "470", "")),
        "current_mortgage": parse_currency(safe_get(combined_data, "17", safe_get(combined_data, "469", 0))),
        "mortgage_provider": safe_get(combined_data, "473", ""),
        "total_property_value": parse_currency(safe_get(combined_data, "468", safe_get(combined_data, "15", 0))),
        "total_property_debt": parse_currency(safe_get(combined_data, "469", safe_get(combined_data, "17", 0))),
        "property_equity": 0.0  # Will be calculated
    }

    # Calculate property equity
    property_assets["property_equity"] = property_assets["current_house_value"] - property_assets["current_mortgage"]

    # KiwiSaver accounts (up to 3 main, 3 partner)
    kiwisaver_accounts = []

    # Try multiple field number variations for KiwiSaver
    # Standard fields: 60-65, 215-217, 222-226, 329
    # Alternative fields: 380-384 (as seen in test form), 388-399
    kiwisaver_field_sets = [
        # Standard set
        ("60", "61", "62"),
        ("63", "64", "65"),
        ("215", "216", "217"),
        ("222", "223", "224"),
        ("225", "226", "329"),
        # Alternative set from test form
        ("380", "381", "382"),
        ("383", "384", "385"),
        ("386", "387", "388"),
        ("391", "392", "393"),
        ("394", "395", "396"),
        ("397", "398", "399"),
    ]

    for provider_field, fund_field, balance_field in kiwisaver_field_sets:
        provider = safe_get(combined_data, provider_field, "")
        fund_type = safe_get(combined_data, fund_field, "")
        balance = parse_currency(safe_get(combined_data, balance_field, 0))

        if provider or balance > 0:
            kiwisaver_accounts.append({
                "owner": "main",
                "provider": provider,
                "fund_type": fund_type,
                "balance": balance
            })

    # Calculate total KiwiSaver balance
    total_kiwisaver = sum(account["balance"] for account in kiwisaver_accounts)

    # Other assets (bank accounts, investments, etc.)
    other_assets = []

    # Define asset field mappings (name_field, value_field)
    asset_fields = [
        ("33", "26"),    # Asset 1
        ("19", "36"),    # Asset 2
        ("35", "34"),    # Asset 3
        ("45", "46"),    # Asset 4
        ("47", "187"),   # Asset 5
        ("186", "48"),   # Asset 6
        ("198", "199"),  # Asset 7
        ("189", "188"),  # Asset 8
        ("192", "193"),  # Asset 9
        ("195", "196"),  # Asset 10
        ("201", "202"),  # Asset 11
        ("204", "205"),  # Asset 12
        ("207", "208"),  # Asset 13
        ("210", "211"),  # Asset 14
        ("213", "214"),  # Asset 15
    ]

    for name_field, value_field in asset_fields:
        asset_name = safe_get(combined_data, name_field, "")
        asset_value = parse_currency(safe_get(combined_data, value_field, 0))

        if asset_name or asset_value > 0:  # Include if either field has data
            other_assets.append({
                "asset_type": asset_name,
                "value": asset_value
            })

    # Calculate total other assets
    total_other_assets = sum(asset["value"] for asset in other_assets)

    # Liabilities (loans, credit cards, etc.)
    liabilities = []

    # Define liability field mappings (name_field, value_field)
    liability_fields = [
        ("70", "71"),  # Liability 1 - description and limit
        ("72", "73"),  # Liability 2
        ("74", "75"),  # Liability 3
        ("76", "77"),  # Liability 4
        ("78", "88"),  # Liability 5
    ]

    for desc_field, amount_field in liability_fields:
        liability_desc = safe_get(combined_data, desc_field, "")
        liability_amount = parse_currency(safe_get(combined_data, amount_field, 0))

        if liability_desc or liability_amount > 0:
            liabilities.append({
                "description": liability_desc,
                "amount": liability_amount
            })

    # Add mortgage as a liability if exists
    if property_assets["current_mortgage"] > 0:
        liabilities.insert(0, {
            "description": f"Mortgage - {property_assets['mortgage_provider'] or 'Primary Residence'}",
            "amount": property_assets["current_mortgage"]
        })

    # Calculate total liabilities
    total_liabilities = sum(liability["amount"] for liability in liabilities)

    # Calculate summary values
    total_assets = (
        property_assets["current_house_value"] +
        total_kiwisaver +
        total_other_assets
    )

    net_worth = total_assets - total_liabilities

    # Build the final structure - lean version for Zapier
    return {
        "section_type": "assets_liabilities",
        "property_value": str(property_assets["current_house_value"]),
        "property_address": property_assets["current_house_address"],
        "property_mortgage": str(property_assets["current_mortgage"]),
        "property_equity": str(property_assets["property_equity"]),
        "kiwisaver_balance": str(total_kiwisaver),
        "kiwisaver_count": len(kiwisaver_accounts),
        "other_assets_value": str(total_other_assets),
        "other_assets_count": len(other_assets),
        "total_liabilities": str(total_liabilities),
        "liability_count": len(liabilities),
        "total_assets": str(total_assets),
        "net_worth": str(net_worth),
        "debt_to_asset_ratio": f"{(total_liabilities / total_assets * 100):.1f}" if total_assets > 0 else "0.0"
    }